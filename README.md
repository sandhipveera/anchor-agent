# Anchor

> **Anchor** is a working placeholder name. The user picks the real one.

**An AI agent that helps autistic adults manage daily life — without
pathologizing them, surveilling them, or stripping their autonomy.**

Anchor is a silent-by-default, text-and-haptic-only Android agent that helps an
autistic adult re-enter tasks after sensory breaks, cook with confidence using
the appliances he actually has, stay safe from scams, and keep manual awareness
of his own money — on his terms. The agent reasons with **Gemini**, remembers
with **Elastic**, persists state in **Firestore**, and acts on the outside world
**only with his explicit approval of the exact action.** He is the user, and he
is in charge.

Built for the **Google Cloud Rapid Agent Hackathon (Elastic partner track).**

📹 **Demo video:** _coming soon_

---

## Who this is for

One person: an autistic adult working toward independent living, phone-only,
Android, sound-sensitive, who communicates by text and tap. Existing assistive
tools were too clinical, too chirpy, too surveillance-heavy, or built for
children. This is built with care, for an adult, by someone who knows him.

Throughout the code and docs he is referred to only as **"the user."** No real
name, ever.

---

## Design principles (the short version)

These are **immutable**. If a feature requires violating one, it does not ship.
Full text — including the exclusions and the reasoning — in
[DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md).

1. He is the user. He is in charge. No caregiver dashboard, no reporting up.
2. Predictable over clever. Same behavior every time.
3. Literal language. No idioms, metaphors, or sarcasm.
4. Silent by default. Haptic-first. No sounds unless he enables them per context.
5. No device voice output by default.
6. Notifications are scarce. Each one must earn its place.
7. Asks before acting on the outside world — exact text/action, every time.
8. No behavior-tracking framing. It bookmarks; it does not surveil.
9. No pathologizing language. Identity-first. No functioning labels.
10. No gamification. No streaks, badges, points, levels.
11. Honest about uncertainty.
12. Privacy is absolute. No analytics, no telemetry, no trackers.
13. Not therapy, not crisis support. Crisis routes only to his sibling, on his
    initiative.
14. Sensory pre-warnings before any loud cooking step. Always.
15. Stovetop (and blender) are invisible unless he turns them on.

**Money principles (16–23):**

16. The agent never moves money, touches a bank, or holds payment credentials.
17. No financial advice. Scam analysis is fraud protection, not advice.
18. No paternalism on spending. No "are you sure?", no imposed friction.
19. Spending and savings data is his eyes only.
20. Scam verdicts are information, not action. He decides; the agent never acts.
21. Spending categorization is suggestive and always overridable, zero friction.
22. Saving goals are user-owned — edit, pause, delete any time, no commentary.
23. Pattern surfacing is neutral. Totals, never verdicts or comparisons.

---

## What is deliberately NOT built

The absences are part of the design — see
[DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md#what-is-deliberately-not-built-and-never-will-be-without-re-opening-this-design).
No voice I/O. No gamification. No caregiver dashboard. No behavior commentary. No
location tracking. No mood/emotion detection. No social features. No time-shaming.
No auto-advance / auto-detect / auto-escalate. No crisis hotlines as a runtime
path. No audio recording of any kind.

**On money, specifically** — the money features are manual-entry and
informational by design. The following are deliberately not built, and won't be
without re-opening the design (see
[The money boundary](./DESIGN_PRINCIPLES.md#the-money-boundary)):

- **No banking integration** (Plaid, Yodlee, or any account aggregator).
- **No auto-pay or money transfers** — the agent never moves money.
- **No spending caps or budget enforcement** — no paternalism on his spending.
- **No financial advice** of any kind — scam analysis is fraud protection, not
  advice.
- **No spending visibility to anyone but the user** — not the sibling, not
  parents, not an aggregated view.

---

## Capabilities

**Daily living**

- **Day Flow Co-pilot** (primary) — holds his place across regulation breaks.
  "Where was I?" reconstructs his task in one screen, literal language, **no time
  or gap commentary.**
- **Cooking Guide** (demo centerpiece) — meals he can make today with the
  appliances he has (microwave, air fryer, toaster oven, instant pot, rice
  cooker, kettle). One step at a time, **sensory pre-warning before any loud
  step**, an "I'm overwhelmed" button that holds his place without judgment.
- **Lifeline** — pre-written editable messages and a "help me word this"
  composer; opens his own SMS app with the exact text. The agent never sends.

**Money awareness** — manual-entry, informational, his-eyes-only. The agent never
touches a bank or moves money (see [The money boundary](./DESIGN_PRINCIPLES.md#the-money-boundary)).

- **Scam Shield** — he pastes suspicious content; **Gemini 2.5 Pro**, grounded in
  a scam-pattern knowledge base (FTC, AARP Fraud Watch, autism-community sources),
  returns a verdict, specific red flags in plain language, recommended actions,
  and *why the manipulation works*. **He decides; the agent does not act** — no
  blocking, no contacting, no notifying. Fraud protection, not financial advice.
- **Bill Awareness** — he defines recurring bills; a haptic reminder fires on the
  due date; he marks paid manually. The agent never pays.
- **Spending Log** — manual entries with user-defined categories (the agent
  suggests a category, he overrides with zero friction). "What did I spend this
  week?" returns **neutral totals** — no commentary, no comparisons, no alerts.
- **Saving Goals** — manual deposit logging shown as **"$X of $Y"** — no progress
  bars that imply pressure, no celebrations. Edit, pause, or delete any time.

> **About the money data in the demo.** The spending and savings figures shown in
> the demo are **illustrative dummy data**. The real implementation requires
> **manual user entry**. **Banking integration is intentionally deferred** to
> protect users from financial-data-handling risk during early development. This
> is a **design choice, not an oversight.**

---

## Architecture

```
[Android PWA]  ──HTTPS──►  [Cloud Run: FastAPI]
   text · haptic                 │
   no sound · no voice           ├─► [Vertex AI ADK on Agent Engine] ─► Gemini 2.5 Flash/Pro
                                 ├─► [Elastic Serverless · Agent Builder MCP] ─► repertoire/memory/knowledge/spending/savings
                                 ├─► [Firestore] ─► task · profile · settings · bills · goals · categories (per-uid)
                                 └─► [Web Push] ─► haptic notifications (no sound)

[Lifeline] ─► opens the user's native SMS app with editable pre-filled text — he sends from his own number
```

Full system design, data model, and rationale in
[ARCHITECTURE.md](./ARCHITECTURE.md). Two deliberate technology choices:

- **Elastic Serverless + the Agent Builder MCP endpoint** (not the deprecated
  standalone `mcp-server-elasticsearch`), so the agent calls intent-level custom
  tools instead of raw Query DSL.
- **Vertex AI ADK on Agent Engine** (not Conversational Agent Builder), for
  first-class tool definitions and a visible reasoning trace.

---

## Security & privacy

This is **health-adjacent, disability-related data**, and we treat it at
HIPAA-adjacent sensitivity even though it is not formally regulated.

- All user data is scoped to his own cloud account and encrypted at rest.
- Every backend query is **hard-pinned to his authenticated identity
  server-side**; client-claimed identity is never trusted.
- Logs are **scrubbed of personal content** — no task text, pantry, pasted scam
  content, spending/bill/goal details, or message bodies in any log line. No
  verbose access logging.
- **Vertex AI does not train on prompts or data by default**
  ([Google's policy](https://cloud.google.com/vertex-ai/generative-ai/docs/data-governance)).
- Semantic memory has a **rolling 90-day retention** and is **deletable by him at
  any time**.
- **No analytics, no telemetry, no third-party trackers** anywhere in the stack.
- The lifeline carries no app branding and routes SMS through his own device — no
  carrier-plaintext routing through our infrastructure.

Details and threat-model notes in
[ARCHITECTURE.md](./ARCHITECTURE.md#security--privacy).

---

## Setup (self-hosting)

> Work in progress — fleshed out as the build proceeds.

**Prerequisites:** Google Cloud project (Vertex AI, Cloud Run, Firestore, Cloud
Build enabled), an Elastic Serverless project (or Stack ≥ 9.2), Node.js + pnpm,
Python 3.12+.

```
# backend
cd backend && uv sync          # or: pip install -e .
# configure env: GCP project, Elastic MCP endpoint + API key, VAPID keys
uvicorn app.main:app --reload

# frontend
cd frontend && pnpm install && pnpm dev
```

Detailed instructions land alongside each phase. The PWA installs on Android via
Chrome's "Add to Home screen."

---

## Repository layout

```
anchor-agent/
├── LICENSE                  # Apache 2.0
├── README.md                # this file
├── DESIGN_PRINCIPLES.md     # the 23 immutable principles (public-facing)
├── ARCHITECTURE.md          # system design, data model, security posture
├── backend/                 # FastAPI on Cloud Run, ADK agent, Elastic client
│   └── seed/                # demo seed fixtures + loader (loader: post-spike)
├── frontend/                # React + TS + Tailwind PWA
└── docs/
    ├── demo-script.md       # 3-minute submission video arc
    └── spikes/              # de-risking experiments (haptic-push first)
```

---

## Acknowledgments

This design is informed by the writing of **autistic adult self-advocates** who
have described, in their own words, what assistive technology gets wrong — the
chirpiness, the surveillance, the infantilization, the false urgency. The best
thing this software can do is get out of the way and hold his place when he asks.

---

## License

[Apache License 2.0](./LICENSE).
