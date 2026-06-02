"""Backend configuration, loaded from environment.

All secrets come from the environment (Cloud Run env vars / Secret Manager in
prod, a local .env in dev — see .env.example). Nothing sensitive is hardcoded.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "anchor"
    environment: str = "dev"  # dev | staging | prod

    # --- Elastic (populated once the Serverless trial is live; see .env.example) ---
    elastic_endpoint_url: str | None = None
    elastic_api_key: str | None = None
    elastic_cloud_id: str | None = None

    # --- Google Cloud ---
    gcp_project: str | None = None

    # --- Auth (Google Sign-In; not wired yet — middleware stub only) ---
    google_client_id: str | None = None

    # --- CORS: comma-separated allowed origins. "*" only acceptable for the
    #     content-free /healthz shell; lock down before any data endpoint. ---
    cors_allow_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
