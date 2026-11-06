"""
App configuration.

Local development uses an embedded libSQL file (100% SQLite-compatible, zero setup).
Production simply points these two env vars at a real Turso database:

    TURSO_DATABASE_URL=libsql://<your-db>-<org>.turso.io
    TURSO_AUTH_TOKEN=<token from `turso db tokens create`>

No code changes are needed to switch — libsql_client speaks the same protocol
to a local file or to Turso's cloud, which is why we picked it.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Student Career Intelligence Platform"

    # Turso / libSQL
    turso_database_url: str = os.getenv("TURSO_DATABASE_URL", "file:local.db")
    turso_auth_token: str = os.getenv("TURSO_AUTH_TOKEN", "")

    # Auth
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    class Config:
        env_file = ".env"


settings = Settings()
