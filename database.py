"""
Thin async wrapper around libsql_client so the rest of the app never has to
think about whether it's talking to a local .db file or a remote Turso
database — same calls, same SQL, either way.
"""
import os
import libsql_client
from pathlib import Path
from .config import settings

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _make_client() -> libsql_client.Client:
    url = settings.turso_database_url
    if url.startswith("file:"):
        # Local embedded mode — no auth token needed.
        return libsql_client.create_client_sync(url=url)
    return libsql_client.create_client_sync(
        url=url,
        auth_token=settings.turso_auth_token,
    )


_client = _make_client()


def get_client() -> libsql_client.Client:
    return _client


def init_db():
    """Create tables if they don't exist yet, and seed reference data."""
    schema_sql = _SCHEMA_PATH.read_text()
    # Strip full-line/trailing "--" comments before splitting on ";" so a stray
    # semicolon inside a comment can never break statement boundaries.
    cleaned_lines = []
    for line in schema_sql.splitlines():
        idx = line.find("--")
        cleaned_lines.append(line[:idx] if idx != -1 else line)
    cleaned_sql = "\n".join(cleaned_lines)
    statements = [s.strip() for s in cleaned_sql.split(";") if s.strip()]
    for stmt in statements:
        _client.execute(stmt)

    _migrate_interview_attempts_columns()

    # Seed job roles once
    result = _client.execute("SELECT COUNT(*) as c FROM job_roles")
    if result.rows[0][0] == 0:
        from .ai.seed_data import JOB_ROLES, INTERVIEW_QUESTIONS

        for role in JOB_ROLES:
            _client.execute(
                "INSERT INTO job_roles (title, description, required_skills) VALUES (?, ?, ?)",
                [role["title"], role["description"], role["required_skills"]],
            )
        for q in INTERVIEW_QUESTIONS:
            _client.execute(
                "INSERT INTO interview_questions (skill, difficulty, question, ideal_answer) VALUES (?, ?, ?, ?)",
                [q["skill"], q["difficulty"], q["question"], q["ideal_answer"]],
            )

    # Seed events once
    result = _client.execute("SELECT COUNT(*) as c FROM events")
    if result.rows[0][0] == 0:
        from .ai.seed_data import SAMPLE_EVENTS

        for ev in SAMPLE_EVENTS:
            _client.execute(
                """INSERT INTO events
                   (title, event_type, organizer, description, mode, location,
                    start_date, registration_deadline, external_url, tags, is_recurring)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    ev["title"], ev["event_type"], ev["organizer"], ev["description"],
                    ev["mode"], ev["location"], ev["start_date"], ev["registration_deadline"],
                    ev["external_url"], ev["tags"], ev["is_recurring"],
                ],
            )


def _migrate_interview_attempts_columns():
    """
    Adds new interview_attempts columns for anyone with a pre-existing local.db
    from before voice/keyword/integrity feedback was added. CREATE TABLE IF NOT
    EXISTS won't retrofit an already-created table, so we patch it here —
    each ALTER is wrapped since libSQL raises if the column already exists.
    """
    new_columns = [
        ("matched_keywords", "TEXT"),
        ("missing_keywords", "TEXT"),
        ("input_mode", "TEXT DEFAULT 'text'"),
        ("flagged_inappropriate", "INTEGER DEFAULT 0"),
        ("integrity_flag", "TEXT DEFAULT 'clean'"),
        ("integrity_reasons", "TEXT"),
    ]
    for name, col_type in new_columns:
        try:
            _client.execute(f"ALTER TABLE interview_attempts ADD COLUMN {name} {col_type}")
        except Exception:
            pass  # column already exists


def query(sql: str, params: list | None = None):
    """Run a SELECT and return list-of-dict rows."""
    rs = _client.execute(sql, params or [])
    cols = rs.columns
    return [dict(zip(cols, row)) for row in rs.rows]


def execute(sql: str, params: list | None = None):
    """Run an INSERT/UPDATE/DELETE. Returns (last_insert_rowid, rows_affected)."""
    rs = _client.execute(sql, params or [])
    return rs.last_insert_rowid, rs.rows_affected
