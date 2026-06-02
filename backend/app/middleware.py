"""Server-side identity pinning — scaffolding (ARCHITECTURE.md §7).

The product is single-user, and **every** Firestore/Elastic query must be
hard-pinned to the server-verified `uid`. Client-claimed identity is never
trusted. Google Sign-In is not wired yet, so this middleware is a stub: it
establishes the contract and the `request.state.uid` surface that capability
code will depend on, without yet verifying tokens.

When auth is wired (next phase):
  1. Read the `Authorization: Bearer <google-id-token>` header.
  2. Verify it with `google.oauth2.id_token.verify_oauth2_token(...)` against
     `settings.google_client_id`.
  3. Set `request.state.uid` to the verified `sub` claim and
     `request.state.authenticated = True`.
  4. Reject (401) protected routes when unauthenticated.

Until then we attach an explicit "not authenticated" marker so no capability
code can accidentally assume an identity.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

# Routes that never require an identity.
_PUBLIC_PATHS = frozenset({"/healthz", "/docs", "/openapi.json", "/redoc"})


class IdentityPinningMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # TODO(auth): verify the Bearer Google ID token and set the real uid.
        auth_header = request.headers.get("authorization", "")
        has_bearer = auth_header.lower().startswith("bearer ")

        # Stub state — deliberately unauthenticated until token verification lands.
        request.state.uid = None
        request.state.authenticated = False
        request.state.auth_presented = has_bearer

        # NOTE: when protected routes exist, gate them here on
        #   request.url.path not in _PUBLIC_PATHS and not request.state.authenticated
        # returning a 401. No such routes exist yet (only /healthz).
        return await call_next(request)
