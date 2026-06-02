# Design Principles

These principles are the spine of this project. They are not guidelines. They
are hard constraints. **If a feature requires violating one of these, the
feature does not ship.**

This document is public and permanent. It exists so that anyone who contributes
to, forks, or audits this project understands *why* the software behaves the way
it does — and, just as importantly, why certain obvious-seeming features are
deliberately absent. The absences are part of the design. Do not "fix" them.

The agent is built for one person: an autistic adult working toward independent
living. Throughout this repo he is referred to only as **"the user."** He is the
user, and he is in charge.

---

## The Immutable Principles

1. **He is the user. He is in charge.**
   Not parents, not caregivers, not the engineer. There is no caregiver
   dashboard, no reporting up, no visibility for anyone but him.

2. **Predictable over clever.**
   The agent behaves the same way every time. No surprise "delight" features. No
   A/B tests. No adaptive UI that shifts beneath him. Sameness is a feature, not
   a limitation.

3. **Literal language.**
   No idioms, no metaphors, no sarcasm. "Take a break," not "step away for a
   sec." "The task is paused," not "we'll come back to this." Every string in the
   product is reviewed against this.

4. **Silent by default.**
   No sounds, ever, unless he explicitly enables them per context. Haptic-first
   for all alerts. There is no global "sound on" toggle that a stray setting
   could flip.

5. **No device voice output by default.**
   Text on screen is primary. If voice is ever offered, it is an explicit
   per-context opt-in, and it is remembered. Person-to-person voice is fine;
   device voice is not.

6. **Notifications are scarce.**
   Each haptic notification must earn its place. The agent is mostly waiting to
   be useful, not pushing. A notification that does not change what he can do
   right now should not fire.

7. **Asks before acting on the outside world.**
   Sending a message, drafting an email, modifying anything outside the app —
   explicit confirmation of the *exact* text or action, every time. No "I went
   ahead and..." Ever.

8. **No behavior tracking framing.**
   The agent holds task state; it does not log "user was away for X minutes" or
   "user got stuck N times today." It bookmarks; it does not surveil. Time gaps
   are never measured, surfaced, or commented on.

9. **No pathologizing language anywhere.**
   Identity-first ("autistic adult"). No functioning labels. No "managing your
   autism." No "behavioral patterns." No clinical terms in user-facing copy.

10. **No gamification.**
    No streaks, badges, points, levels, celebrations, or progress bars that
    imply judgment. Completing a task is its own outcome.

11. **Honest about uncertainty.**
    "I'm not sure if this message is a scam — here's what looks off" beats false
    confidence. The agent says when it doesn't know.

12. **Privacy is absolute.**
    All user data is scoped to his own cloud account, encrypted at rest. No
    analytics. No telemetry beyond what the agent operationally needs to
    function. No third-party trackers. (See [SECURITY & PRIVACY](#security--privacy-posture).)

13. **The agent is not therapy and not crisis support.**
    It supports daily living. Crisis paths route only to his sibling lifeline,
    which *he* initiates — not to hotlines, not to auto-escalation. (See
    [The distress-silence design](#the-distress-silence-design).)

14. **Sensory pre-warnings before any loud step.**
    In cooking flows, always. A full-screen pre-warning fires before any loud
    appliance step, with the choice to proceed, wait, or skip. Non-negotiable.

15. **Stovetop is invisible.**
    Unless he explicitly turns it on. Do not suggest it. Do not "encourage" it.
    Do not include it in default recipes. The same applies to the blender: he has
    not used one and does not want to — it does not appear.

### Money principles (16–23)

The money-management capabilities add eight more constraints. They are as
immutable as the first fifteen. See [The money boundary](#the-money-boundary) for
why these exist as hard lines.

16. **The agent never moves money.**
    It never accesses bank accounts, never holds payment credentials, never
    initiates a transfer or a payment. No exceptions. The agent records and
    informs; the user acts, with his own hands, in his own apps.

17. **No financial advice.**
    No investment, credit, tax, or budgeting advice. Scam analysis is *fraud
    protection*, not financial advice — it explains what looks deceptive, not what
    he should do with his money.

18. **No paternalism on spending.**
    The agent never tells him what to buy, never asks "are you sure?", never
    imposes friction or a cooling-off step. What he spends is his business.

19. **Spending and savings data is his eyes only.**
    Not the sibling, not parents, not any aggregated or shared view. The same
    privacy wall as everything else (§1, §12), stated explicitly for money.

20. **Scam verdicts are information, not action.**
    The agent presents its analysis; he decides. Even on "very likely scam," the
    agent does not block, does not contact anyone, does not notify anyone, does
    not take any protective action on his behalf.

21. **Spending categorization is suggestive and always overridable.**
    The agent may suggest a category; he can override it with zero friction. No
    "are you sure" on an override. His category wins, always, instantly.

22. **Saving goals are user-owned.**
    Edit, pause, or delete any goal at any time, with zero commentary on the
    change. No "are you sure you want to give up?", no disappointment framing, no
    record of abandoned goals.

23. **Pattern surfacing is neutral.**
    When the agent shows spending or savings data, it shows data — never
    interpreted as "good" or "bad," never compared to other people or to past
    periods as judgment, never framed as a problem. Totals, not verdicts.

---

## The distress-silence design

This is the principle most likely to be "helpfully" broken by a future
contributor. Read this before you touch the lifeline.

When the user uses the **"help me word this"** composer and what he types reads
as distress, the agent helps him word **exactly what he asked to word.** That is
all.

- **No** keyword scanning for crisis language.
- **No** soft nudge toward a resource.
- **No** pop-up of hotlines.
- **No** behavioral redirect.
- **No** change in tone, pacing, or available options.

The lifeline channel *is* the design's crisis path. If he is using it, the
system is already working as intended. Adding a runtime "safety net" would:

- violate **Predictability** (§2) — the agent would suddenly behave differently
  at the worst possible moment;
- **pathologize** him (§9) — treating his words as symptoms to be flagged;
- have the agent doing **amateur psychiatry it is not qualified for** (§13).

### The one and only disclosure

There is exactly one place where crisis information appears: a **one-time
onboarding screen**, shown once at first launch, stating plainly:

> This is not therapy or crisis support. If you are in crisis, here are
> resources: [list]. You can message [sibling] anytime using the lifeline.

He acknowledges it. The screen never appears again. The agent never references
it at runtime, never re-surfaces it, never "checks in." Disclosure happens once,
honestly, up front — and then autonomy is absolute.

This is the balance: **disclose once, then trust completely.** Do not move the
disclosure into the runtime. Do not repeat it. Do not make it conditional on
what he types.

---

## The money boundary

The money-management capabilities (scam shield, bill awareness, spending log,
saving goals) help him stay aware of his own money. They never touch it.

**The agent is a notebook and a second pair of eyes — not a wallet, not a bank,
not an advisor.** Concretely:

- It **never** connects to a bank, payment processor, or card. There is no
  Plaid/Yodlee/aggregator integration, by design (§16).
- It **never** holds a credential that could move money.
- It **never** pays a bill, transfers funds, or enforces a budget cap.
- It **never** gives financial advice. The scam shield protects against *fraud*;
  it does not tell him what to do with his money (§17).
- It **never** judges his spending or imposes friction on it (§18, §23).
- It **never** shows his money to anyone but him (§19).

Every money feature is **manual-entry and informational.** Banking integration is
deliberately deferred — not because it's hard, but because handling someone's
financial data carries real risk we will not take on during early development.
That deferral is a design choice, documented as such, not an oversight or a TODO.

If a future contributor proposes letting the agent "just pay the bill for him" or
"link his account so he doesn't have to type," the answer is no, and this section
is why.

---

## What is deliberately NOT built (and never will be without re-opening this design)

These are not "v1 cut for time." They are **excluded by design.** Building any of
them requires re-opening this document and the conversation behind it.

- ❌ **Voice input or output** — he doesn't want it.
- ❌ **Gamification** — streaks, badges, points, levels, celebratory animations.
- ❌ **Parent-facing dashboard** or any caregiver visibility whatsoever.
- ❌ **Behavior commentary** — "We noticed you've been..." and anything like it.
- ❌ **Location tracking.**
- ❌ **Automatic mood / emotion detection.**
- ❌ **Social features** or sharing to social media.
- ❌ **Time-shaming language** — "you've been away for 14 minutes."
- ❌ **Auto-advance, auto-detect-stuck, or auto-escalate logic** — every step
  transition is an explicit tap.
- ❌ **Crisis hotlines as a runtime path** — he routes to his sibling only, on
  his own initiative (see above).
- ❌ **Audio recording of any kind** — would violate §4, §5, §8, and §12 at once.

### On money, specifically (see [The money boundary](#the-money-boundary))

- ❌ **Banking integration** (Plaid, Yodlee, or any account aggregator) —
  handling financial data carries real risk we will not take on in early
  development. Manual entry only. This is a design choice, not an oversight.
- ❌ **Auto-pay or money transfers** — the agent never moves money (§16).
- ❌ **Spending caps or budget enforcement** — no paternalism on his spending
  (§18).
- ❌ **Financial advice of any kind** — investment, credit, tax, budgeting. Scam
  analysis is fraud protection, not advice (§17).
- ❌ **Spending visibility to anyone but the user** — not the sibling, not
  parents, not an aggregated view (§19).

---

## How to use this document as a contributor

Before adding any feature, ask:

1. Does it let the agent act on the outside world without explicit confirmation
   of the exact action? → It doesn't ship (§7).
2. Does it measure, store, or surface a time gap or a behavior count? → It
   doesn't ship (§8).
3. Does it make the UI behave differently than it did yesterday? → It doesn't
   ship (§2).
4. Does it put information in front of anyone other than the user? → It doesn't
   ship (§1, §12).
5. Does it treat his words or behavior as symptoms? → It doesn't ship (§9, §13).

When in doubt, choose the option that gives him more control and less
observation. That choice is almost always correct here.

---

## Security & privacy posture

Privacy here is not a checkbox; it is principle §12, and this is health-adjacent,
disability-related data. The full technical posture lives in
[ARCHITECTURE.md](./ARCHITECTURE.md#security--privacy). In summary:

- Data is scoped to the user's own cloud account and encrypted at rest.
- Every backend query is hard-pinned to the authenticated user server-side;
  client-claimed identity is never trusted.
- Request/response logs are scrubbed of personal content; the system logs only
  what it operationally needs.
- The reasoning model (Vertex AI / Gemini) does not train on the user's prompts
  or data.
- The semantic memory index has a rolling retention window and is deletable by
  the user at any time.
- There is no analytics, no telemetry, and no third-party tracker anywhere in
  the stack.

---

## Acknowledgment

This design is informed by the writing of autistic adult self-advocates who have
described, in their own words, what assistive technology gets wrong: the
chirpiness, the surveillance, the infantilization, the false urgency. The best
thing this project can do is get out of the way and hold his place when he asks.
