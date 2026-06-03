"""Anchor backend — FastAPI app entrypoint.

Phase-0 surface: a single /healthz endpoint. The security scaffolding
(identity-pinning middleware, PII-scrubbing + no-access-log logging) is wired in
now so capability code inherits it from day one. See ARCHITECTURE.md §4, §7.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .logging_config import configure_logging
from .middleware import IdentityPinningMiddleware

configure_logging()
settings = get_settings()

app = FastAPI(
    title="Anchor backend",
    description="Silent-by-default, single-user assistive agent backend.",
    version="0.1.0",
)

app.add_middleware(IdentityPinningMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


# Served at BOTH paths: `/healthz` follows the k8s convention and is reachable
# locally / behind a custom domain or load balancer; `/health` is the path that
# reaches the container on the bare *.run.app URL, because Google Front End
# reserves and intercepts `/healthz` there. Content-free by design — safe to log.
@app.get("/healthz")
@app.get("/health")
def healthz() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "service": settings.service_name}
