# Architecture

This document describes the system design, data model, agent layer, and security
posture for the Anchor agent. It is the technical companion to
[DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md). Where the two ever appear to
conflict, the principles win and this document is wrong and must be fixed.

> **Naming note:** "Anchor" is a working placeholder. The user picks the real
> name.

---

## 1. System overview

A single-user, silent-by-default, text-and-haptic-only Android **Progressive Web
App** backed by a stateless Python service on Google Cloud. The agent reasons
with **Gemini**, remembers with **Elastic**, persists simple state in
**Firestore**, and acts on the outside world only with the user's explicit
confirmation of the exact action.

```
                         ┌──────────────────────────────┐
                         │      Android device          │
                         │  ┌────────────────────────┐  │
                         │  │  PWA (React + TS + TW)  │  │
                         │  │  dark · low-motion ·    │  │
                         │  │  one thing on screen    │  │
                         │  └───────────┬────────────┘  │
                         │  Web Push (haptic, no sound)  │
                         │  Native SMS app (lifeline)    │
                         └──────────────┼────────────────┘
                                        │ HTTPS (Google Sign-In, ID token)
                                        ▼
                         ┌──────────────────────────────┐
                         │  Cloud Run: FastAPI backend   │
                         │  stateless · uid-pinned       │
                         └───┬───────────┬───────────┬───┘
                             │           │           │
        ┌────────────────────┘           │           └───────────────────┐
        ▼                                ▼                               ▼
┌─────────────────┐          ┌────────────────────────┐       ┌──────────────────┐
│ Vertex AI       │          │  Elastic (Serverless)  │       │   Firestore      │
│ ADK on Agent    │  tool    │  Agent Builder MCP      │       │  current_task    │
│ Engine          │◄────────►│  endpoint               │       │  profile         │
│ Gemini 2.5      │  calls   │  repertoire · memory ·  │       │  settings        │
│ Flash / Pro     │          │  knowledge indices      │       │  (per-uid)       │
└────────┬────────┘          └────────────────────────┘       └──────────────────┘
         │
         ▼
┌─────────────────┐
│ Vertex AI       │
│ embeddings      │
│ gemini-         │
│ embedding-001   │
└─────────────────┘
```

There is **no Twilio / third-party SMS provider** and **no caregiver-facing
surface** of any kind. The lifeline opens the user's own native SMS app with
pre-filled, editable text; he sends from his own number.

---

## 2. Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Frontend | PWA — React + TypeScript + Tailwind, Vite | Dark by default, high contrast, low motion, large tap targets, one thing on screen. |
| Backend | Python **FastAPI** on **Cloud Run** | Stateless. All user state in Firestore + Elastic. |
| Agent layer | **Vertex AI ADK** (Agent Development Kit) deployed to **Agent Engine** | First-class tool definitions + visible reasoning trace. See §4. |
| Custom tool handlers | **Vertex AI Python SDK** | For logic where a managed tool is too constrained. |
| Reasoning model | **Gemini 2.5 Flash** (default), **Gemini 2.5 Pro** (JD decode, pattern surfacing) | Via Vertex AI. |
| Embeddings | **`gemini-embedding-001`** — version pinned | Changing the model invalidates indices; never bump silently. |
| Semantic memory | **Elastic Serverless** (Stack ≥ 9.2 equivalent) | Connected via the **Agent Builder MCP endpoint**, not the deprecated standalone server. See §5. |
| Persistent state | **Firestore** | current_task, profile, settings — per uid. |
| Auth | **Google Sign-In**, single user | uid enforced server-side. See §7. |
| Notifications | **Web Push** (haptic + visual, no sound) | Android-only target. Viability under validation — see §8. |
| Lifeline | **Native SMS deep-link** (`sms:` URI) | No third-party provider. He sends from his own device. |
| Hosting | Cloud Run (backend) + Firebase Hosting (PWA) | |

### Why these two decisions

- **Elastic Serverless + Agent Builder MCP, not the standalone server.** The
  standalone `elastic/mcp-server-elasticsearch` is deprecated as of Elastic 9.2 /
  Cloud Serverless and receives security-only updates. It is also read-only
  (`list_indices`, `get_mappings`, `search`, `esql`, `get_shards`) — it has no
  write/index tool. The **Agent Builder MCP endpoint** exposes built-in *and
  custom* tools defined server-side in Elastic, so the agent calls a single
  semantic tool (e.g. `search_repertoire`) instead of hand-authoring Query DSL.
  Non-deprecated, cleaner, and a stronger Elastic-partner-track demo.

- **ADK on Agent Engine, not Conversational Agent Builder.** Google's
  Conversational Agents / "Agent Builder" umbrella is a search/RAG/dialog app
  builder — weak for explicit, auditable tool-calling. **ADK** gives first-class
  tool definitions and a **visible reasoning trace**, which is required both for
  the JD-decoder demo ([capabilities §C](#92-capability-c--job-search-slice)) and
  for the "Technological Implementation" judging criterion.

---

## 3. Data model

### Firestore (non-semantic state)

```
users/{uid}/profile
  preferences, sensory profile, sibling contact (name only; number stays in his
  own phone contacts), voice/writing samples (TEXT ONLY — no audio, ever),
  opt-ins, onboarding_disclosure_acknowledged (bool)

users/{uid}/current_task          # single active task, or null
  task_id, task_name, steps[], current_step_index,
  status (active|paused|complete), started_at, last_interaction_at, notes

users/{uid}/settings
  notification timing windows, haptic preferences, language directness level,
  enabled capabilities (per-context opt-ins, e.g. stovetop, sound)
```

`started_at` / `last_interaction_at` exist for ordering and task continuity
**only**. They are **never** differenced into a "time away" value, never
surfaced, never reasoned over for gap commentary (§8).

### Elastic indices (semantic memory)

| Index | Documents | Purpose |
|---|---|---|
| **`repertoire`** | `{user_id, type: "meal"\|"routine", name, description, appliance_used[], tags[], last_done_at, success_count, embedding}` | "What can I make right now?" — semantic search over meals/routines he has done. |
| **`memory`** | `{user_id, timestamp, event_type, task_id, content, tags[], embedding}` | "Where was I?" reconstruction. **Rolling 90-day retention, user-deletable any time.** |
| **`knowledge`** | `{type, content, tags[], source, embedding}` | Seeded reference: autism-friendly employer signals, accommodation language, confirmed-helpful regulation strategies, pre-written lifeline messages. |

All embeddings via `gemini-embedding-001` (pinned). Writes go through the Elastic
Python client (the MCP retrieval path is read-only by design); reads go through
the Agent Builder MCP tools.

---

## 4. Agent layer (ADK on Agent Engine)

The agent is a tool-calling reasoning loop. The PWA never talks to Gemini
directly — it calls the FastAPI backend, which invokes the ADK agent. Tools are
defined per capability and the reasoning trace (plan + tool calls) is captured
and can be surfaced in the UI for the job-search demo.

### Tool surface (by capability)

**Day Flow** — `set_current_task`, `mark_step_complete`, `where_was_i`,
`pause_task`, `resume_task`, `end_task`, `schedule_haptic`.

**Cooking** — `list_pantry`, `update_pantry`, `suggest_meals`, `start_meal`,
`next_step`, `pre_warn_sound`, `simplify`, `save_meal_to_repertoire`.

**Job Search** — `decode_job_posting` (Gemini Pro), `draft_application`
(never sends — drafts only; he sends from his own email app).

**Lifeline** — composes exact text and hands it to the native SMS app; the agent
never transmits.

### Hard rules enforced in the agent loop

- `where_was_i()` output contains **no time references and no gap commentary**.
- No tool auto-advances a step; every transition is an explicit user action.
- Any tool that would touch the outside world returns a *proposal* for explicit
  confirmation, never a completed action (§7).
- `pre_warn_sound` fires before any loud appliance step (§14), full-screen, with
  "I'm ready" / "give me a minute" / "skip this step if possible".

---

## 5. Elastic integration (Agent Builder MCP)

- Provision Elastic as **Serverless** (or Stack ≥ 9.2).
- Define custom tools in **Agent Builder** server-side (e.g. `search_repertoire`,
  `search_memory`, `lookup_knowledge`) so the agent calls intent-level tools, not
  raw DSL.
- Connect the ADK agent as an **MCP client** to the Agent Builder MCP endpoint
  (URL + API-key header; exact tool list confirmed against the live deployment
  version during Phase 0/2).
- Indexing/seeding (`repertoire`, `knowledge`, and ongoing `memory` writes) uses
  the Elastic Python client directly — the MCP path is retrieval-only.

---

## 6. Lifeline (no third-party SMS)

Single screen, 4–6 pre-written editable messages plus a "help me word this"
composer. Flow:

1. He taps a message or types one.
2. The agent shows the **exact text** that will be sent.
3. Two actions: open SMS to **[sibling]**, or cancel.
4. On confirm, the app opens the native SMS app via an `sms:` deep-link with the
   text pre-filled. **He** presses send, from **his** number.

The agent never transmits anything to anyone. The sibling's phone number lives in
his own device contacts; the backend stores at most a display name. See the
[distress-silence design](./DESIGN_PRINCIPLES.md#the-distress-silence-design) for
why the composer does no crisis detection.

---

## 7. Security & privacy

This is **health-adjacent, disability-related data.** We treat it at
HIPAA-adjacent sensitivity even though it is not formally regulated, and we say so
publicly because it is a credibility item, not just a control.

| Concern | Posture |
|---|---|
| **Data classification** | Sensitive disability-adjacent. Documented here and in the README. Minimize collection; store only what a capability needs. |
| **Single-user enforcement** | Every Firestore/Elastic query is **hard-pinned to the authenticated `uid` server-side.** Client-claimed identity is never trusted. Firestore security rules scoped to `uid`. |
| **Encryption at rest** | All user data scoped to the user's cloud account and encrypted at rest (GCP + Elastic defaults, verified). |
| **Logging vs. §12** | Cloud Run logs requests by default. We **scrub PII** from request/response logs, disable verbose access logging, and document what is logged and why. No log line should contain task content, pantry, JD text, or lifeline message bodies. |
| **Model data governance** | **Vertex AI does not train on prompts or data by default.** Stated in README with citation. No user content leaves the GCP/Elastic trust boundary except as embeddings within Vertex. |
| **Web Push subscription** | The push endpoint is a **capability URL** = a credential. Encrypted at rest in Firestore, never logged, rotated on re-subscribe. VAPID private key in secret storage. |
| **Lifeline PII** | No sibling phone number stored server-side; SMS leaves via the user's own device. No carrier-plaintext routing through our infrastructure. |
| **Retention** | `memory` index: rolling 90 days. User can delete all semantic memory at any time from settings. |
| **No telemetry** | No analytics, no third-party trackers, no behavioral metrics. Operational logging only, PII-scrubbed. |
| **Auth** | Google Sign-In; backend validates the ID token on every request. |

### Threat-model notes

- The most sensitive disclosure risk is **inference**: anything that reveals he
  uses an assistive tool. This is why the lifeline carries no app branding and
  why logs carry no content.
- The second risk is **scope creep into surveillance**: a future "helpful"
  feature that totals time or counts events. §8 of the principles forbids it; code
  review must reject it.

---

## 8. The load-bearing unknown: silent + haptic Web Push on Android PWA

"Silent by default, haptic-first" (§4, §5) depends on behavior we must validate
**before** building capabilities, because it could reshape the product.

The risk: on Android, notification **sound/vibration is governed by OS
notification channels**, and a PWA has less control over channel configuration
than a native app. A background Web Push wakes the service worker, but vibration
comes from the **system notification**, not `navigator.vibrate()` (which only
works while the page is foregrounded). Custom background vibration *patterns* may
be unreliable.

**Mitigation:** a throwaway spike (Phase 0, before the FastAPI hello world)
validated on a real Android device. Fallbacks if it can't be made reliable:

- **(a)** accept foreground-only haptics and design interaction patterns around
  it; or
- **(b)** wrap as a **TWA (Trusted Web Activity)** for Android-only deployment to
  get native notification-channel control.

The spike result is reviewed before choosing. See
[`docs/spikes/haptic-push/`](./docs/spikes/haptic-push/).

---

## 9. Capabilities (summary)

Full behavior in [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md) and the kickoff
doc. Three capabilities:

### 9.1 Capability A — Day Flow Co-pilot (primary)
Hold his place across regulation breaks. `where_was_i()` reconstructs current
task state in one screen, literal language, **no time or gap commentary.**

### 9.2 Capability C — Job Search slice (agentic-reasoning proof)
`decode_job_posting` (Gemini Pro) extracts must-haves, likely-negotiables, red
flags, and autism-friendly signals (matched against the `knowledge` index).
`draft_application` writes in his register from **text** writing samples. The
**reasoning trace is surfaced in the UI** so judges see the agent think. The agent
never sends.

### 9.3 Capability B — Cooking Guide (demo centerpiece)
Appliance-only (microwave, air fryer, toaster oven, instant pot, rice cooker,
kettle). **Never blender. Never stovetop unless explicitly enabled.** One step at
a time, never auto-advance, sensory pre-warning before any loud step.

---

## 10. Build sequence (current)

0. **Foundation** — docs (LICENSE ✓, README, DESIGN_PRINCIPLES ✓, ARCHITECTURE ✓)
   → **haptic-push spike on real Android** → spike report → FastAPI hello world →
   PWA shell → Elastic Serverless provisioning → ADK integration.
1. Capability A (Day Flow).
2. Capability B (Cooking).
3. Capability C (Job Search slice).
4. Lifeline + accessibility/sensory audit + polish.
5. Submission (3-min video, Devpost, README polish, roadmap of deliberate
   absences).
