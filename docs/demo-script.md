# Demo Video Script (~3 minutes)

**Format:** screen recording + voiceover. **No on-camera user.** No real name —
"the user" throughout. Silent UI on screen (haptics can't be shown, so the
voiceover names them). All money figures are illustrative dummy data.

**Goal for judges:** show the agent *reasoning, planning, and taking action* —
while making the deliberate restraint (silence, no surveillance, no money
handling) legible as design, not omission.

| Time | Beat | On screen | Voiceover (literal, calm) |
|---|---|---|---|
| **0:00–0:20** | Hook + motivation | Title card → one-line mission → the user's profile in a sentence. | "This is an agent for an autistic adult living independently. It is silent by default, text and haptic only. It never surveils him, never reports to anyone, and never acts without his say-so." |
| **0:20–0:50** | Cooking start | "What can I make right now?" → pantry input → 2–3 meal options from his repertoire → pick → step 1 → step 2 (one step on screen at a time). | "He asks what he can make. The agent searches what he's cooked before in Elastic, matched to the appliances he actually has — no stovetop, no blender. He picks. One step at a time." |
| **0:50–1:15** | Mid-meal break → re-entry | App left idle → return → tap **"Where was I?"** → one-screen reconstruction: task, current step, inflight state, next step. **No time shown.** | "He steps away to regulate. That's not a problem to fix. When he comes back, 'Where was I?' holds his place — what step, what's in progress, what's next. No mention of how long he was gone." |
| **1:15–1:35** | Sensory pre-warning → simplify → done | Full-screen **pre-warning** before a loud appliance step → "I'm ready / give me a minute / skip if possible" → (optional **Simplify** tap) → meal complete, no celebration. | "Before anything loud, a full-screen warning — his choice to proceed, wait, or skip. If it's too much, 'Simplify' drops to a safe stopping point and holds his place. The meal finishes. No fanfare." |
| **1:35–2:15** | **Scam Shield** (reasoning showcase) | Paste a phishing/smishing text → **Gemini 2.5 Pro** analysis with **visible reasoning trace + tool calls to Elastic knowledge** → verdict (*very likely scam*) → red flags with plain explanations → recommended actions → "why this manipulation works". | "He pastes a message he's unsure about. Gemini Pro reasons over it, grounded in scam patterns from the FTC and AARP. You can see the agent think and call its tools. Verdict: very likely a scam. Here's exactly what's wrong, in plain language, and why it's designed to fool people. The agent tells him. It does not block it, report it, or contact anyone. He decides." |
| **2:15–2:35** | Money awareness | Bill calendar with a **haptic-reminder** due bill → neutral **spending view**: totals by category, no commentary → a **saving goal** as "$X of $Y", no progress-pressure. | "Bills he entered himself remind him with a haptic tap; he marks them paid. Spending he logged shows as plain totals — no judgment, no comparisons. A saving goal is just dollars of dollars. The agent never touches a bank. It's a notebook, not a wallet." |
| **2:35–2:50** | Architecture | Diagram: Gemini 2.5 Flash/Pro → **Vertex AI ADK on Agent Engine** → **Elastic Agent Builder MCP** → **Cloud Run** + Firestore. | "Gemini Flash and Pro reason through Vertex AI's ADK on Agent Engine. Memory and scam knowledge live in Elastic, reached over the Agent Builder MCP endpoint. The backend runs on Cloud Run." |
| **2:50–3:00** | Deliberate absences | Card listing the absences. | "What it doesn't do is the design: no voice, no surveillance, no caregiver dashboard, no money handling, no advice. He is the user. He is in charge." |

## Notes for recording

- **Haptics are invisible on screen** — name each one in voiceover at the moment
  it would fire.
- **Scam Shield is the agentic centerpiece.** Spend the full 40 seconds; make the
  reasoning trace and the Elastic tool calls clearly visible — this is the
  "Technological Implementation" proof.
- Use a **fabricated** phishing sample (no real brand, no real number).
- All spending/savings numbers are dummy data; don't imply they're real.
- Keep on-screen text large and dark-themed to match the product; no motion
  flourishes.
- Target ~2:55 to leave buffer under 3:00.
