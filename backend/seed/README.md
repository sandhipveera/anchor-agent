# Demo seed data

Static JSON fixtures for the demo, plus (later) a loader that indexes them into
Firestore and Elastic.

> **All money figures here are illustrative dummy data.** The real product
> requires manual user entry. There is no banking integration, by design — see
> [The money boundary](../../DESIGN_PRINCIPLES.md#the-money-boundary).

## Status

- **Fixtures** (`data/*.json`) — present now. Static data, safe to commit.
- **Loader** (`load.py`) — **deferred until the haptic-push spike resolves** and
  the PWA-vs-TWA decision is made. The loader depends on the Firestore + Elastic
  clients (capability code), which the current build gate forbids starting. See
  [ARCHITECTURE.md §11](../../ARCHITECTURE.md#11-build-sequence-current).

## Fixtures

| File | Target | Notes |
|---|---|---|
| `data/meals.json` | Elastic `repertoire` | Appliance-only meals. No stovetop, no blender. |
| `data/bills.json` | Firestore `users/{uid}/bills` | 4–5 example bills, varied due dates. |
| `data/savings_goals.json` | Firestore `users/{uid}/savings_goals` | 2–3 goals at varying progress. |
| `data/spending.json` | Elastic `spending` | ~30 days of fictional entries, realistic categories. |
| `data/savings_deposits.json` | Elastic `savings_deposits` | Manual deposits; sums match each goal's `deposits_total`. |
| `data/categories.json` | Firestore `users/{uid}/categories` | The user-defined categories the spending uses. |
| `data/scam-knowledge.json` | Elastic `knowledge` (`type: "scam"`) | Scam patterns from FTC, AARP Fraud Watch, autism-community sources; each has a `source`. |
| `data/lifeline-messages.json` | Elastic `knowledge` (`type: "lifeline"`) | Pre-written lifeline messages. |

## Loader contract (to implement post-spike)

`load.py` will:

1. Read each fixture.
2. Compute embeddings with **`gemini-embedding-001`** (pinned) for indices that
   need them (`repertoire`, `spending`, `knowledge`).
3. Upsert into Elastic via the Elastic Python client (the MCP path is
   retrieval-only) and into Firestore for `bills` / `savings_goals` /
   `categories`.
4. Pin everything to a single demo `uid` passed as an argument.

It must **never** write anything that could move money and must scrub fixture
content from its own logs, consistent with the security posture.

## Sourcing note (scam knowledge)

`scam-knowledge.json` paraphrases publicly available consumer-fraud guidance for
research/demo use. `source` records origin (FTC consumer alerts, AARP Fraud
Watch, autism-community scam reports). Before any real deployment, re-verify each
pattern against the current primary source.
