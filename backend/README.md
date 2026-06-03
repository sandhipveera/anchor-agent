# Anchor backend

FastAPI service for the Anchor agent. Stateless; all user state lives in
Firestore + Elastic (see [ARCHITECTURE.md](../ARCHITECTURE.md)).

## Phase-0 surface

- `GET /healthz` **and** `GET /health` → `{"status": "ok", "service": "anchor"}`
  - Same payload at both. `/healthz` follows the k8s convention and works
    locally / behind a custom domain or load balancer. **On the bare `*.run.app`
    URL, Google Front End reserves and intercepts `/healthz`** before it reaches
    the container, so use **`/health`** there (the frontend does).
- Security scaffolding wired from day one: identity-pinning middleware stub
  (`app/middleware.py`), PII-scrubbing + no-access-log logging
  (`app/logging_config.py`).

## Run locally

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
curl localhost:8080/healthz   # {"status":"ok","service":"anchor"}
```

## Container

```bash
docker build -t anchor-backend .
docker run -p 8080:8080 anchor-backend
```

## Deploy to Cloud Run (from source, no local Docker needed)

```bash
gcloud run deploy anchor-backend \
  --source . \
  --region <REGION> \
  --project <PROJECT_ID> \
  --allow-unauthenticated      # /healthz is public; lock down data routes later
```

Cloud Run sets `$PORT`; the container binds it. Per-request access logging is
disabled (`--no-access-log`) and logs are PII-scrubbed, per ARCHITECTURE.md §7.

## Config

See [`.env.example`](./.env.example). Nothing there is required for `/healthz`;
the Elastic / GCP / auth vars are placeholders for upcoming phases.
