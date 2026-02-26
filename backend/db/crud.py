"""
backend/db/crud.py
------------------
PostgreSQL CRUD layer for the `b2b_leads` table.
Connects via DATABASE_URL environment variable — works in both:
  - Docker:  DATABASE_URL=postgresql://user:pass@db:5432/dbname  (host = db service)
  - Local:   DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Generator

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

TABLE = "b2b_leads"


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def _get_dsn() -> str:
    """Read DATABASE_URL from environment. Fail early with a clear message."""
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set.\n"
            "  Docker format:  postgresql://user:pass@db:5432/dbname\n"
            "  Local format:   postgresql://user:pass@localhost:5432/dbname"
        )
    return dsn


@contextmanager
def _get_conn() -> Generator[psycopg2.extensions.connection, None, None]:
    """Context-managed connection that auto-commits and always closes."""
    conn = psycopg2.connect(_get_dsn(), cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema initialisation (called on app startup)
# ---------------------------------------------------------------------------

def init_db(schema_path: str | None = None) -> None:
    """
    Execute schema.sql to create tables if they don't exist.
    Safe to call multiple times (all statements use IF NOT EXISTS).
    """
    if schema_path is None:
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(schema_path, "r") as f:
        sql = f.read()

    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

    print("[DB] Schema initialised successfully.")


# ---------------------------------------------------------------------------
# CRUD Class
# ---------------------------------------------------------------------------

class SupabaseCRUD:
    """
    CRUD operations for b2b_leads.
    Name kept as SupabaseCRUD for backwards-compatibility with agent code.
    Now backed by psycopg2 + PostgreSQL.
    """

    # -----------------------------------------------------------------------
    # CREATE
    # -----------------------------------------------------------------------

    def create_lead(self, data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new lead. data must include company_name and website_url."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"%({k})s" for k in data.keys())
        sql = (
            f"INSERT INTO {TABLE} ({columns}) VALUES ({placeholders}) "
            "RETURNING *"
        )
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, data)
                return dict(cur.fetchone())

    # -----------------------------------------------------------------------
    # READ
    # -----------------------------------------------------------------------

    def get_lead_by_id(self, lead_id: str) -> dict[str, Any] | None:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {TABLE} WHERE id = %s", (lead_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def get_lead_by_url(self, website_url: str) -> dict[str, Any] | None:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM {TABLE} WHERE website_url = %s", (website_url,)
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def list_leads(
        self,
        status: str | None = None,
        is_approved: bool | None = None,
        blacklisted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        conditions = ["blacklisted = %s"]
        params: list[Any] = [blacklisted]

        if status is not None:
            conditions.append("lead_status = %s")
            params.append(status)
        if is_approved is not None:
            conditions.append("is_approved = %s")
            params.append(is_approved)

        where = " AND ".join(conditions)
        sql = (
            f"SELECT * FROM {TABLE} WHERE {where} "
            f"ORDER BY created_at DESC LIMIT %s OFFSET %s"
        )
        params += [limit, offset]

        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return [dict(r) for r in cur.fetchall()]

    # -----------------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------------

    def update_lead(self, lead_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        set_clause = ", ".join(f"{k} = %({k})s" for k in updates.keys())
        sql = f"UPDATE {TABLE} SET {set_clause} WHERE id = %(id)s RETURNING *"
        params = {**updates, "id": lead_id}
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return dict(cur.fetchone())

    def update_lead_status(self, lead_id: str, new_status: str) -> dict[str, Any]:
        return self.update_lead(lead_id, {"lead_status": new_status})

    def approve_lead(self, lead_id: str) -> dict[str, Any]:
        return self.update_lead(lead_id, {"is_approved": True, "lead_status": "Approved"})

    def set_icebreaker(self, lead_id: str, text: str) -> dict[str, Any]:
        return self.update_lead(lead_id, {"icebreaker_text": text})

    def set_company_context(self, lead_id: str, context: str) -> dict[str, Any]:
        return self.update_lead(lead_id, {"company_context": context})

    def blacklist_lead(self, lead_id: str) -> dict[str, Any]:
        return self.update_lead(
            lead_id, {"blacklisted": True, "lead_status": "Blacklisted"}
        )

    def increment_daily_send(self, lead_id: str) -> dict[str, Any]:
        sql = (
            f"UPDATE {TABLE} SET daily_send_count = daily_send_count + 1, "
            "last_contact_date = NOW() WHERE id = %s RETURNING *"
        )
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (lead_id,))
                return dict(cur.fetchone())

    # -----------------------------------------------------------------------
    # DELETE
    # -----------------------------------------------------------------------

    def delete_lead(self, lead_id: str) -> bool:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {TABLE} WHERE id = %s", (lead_id,))
                return cur.rowcount > 0

    # -----------------------------------------------------------------------
    # UPSERT
    # -----------------------------------------------------------------------

    def upsert_lead(self, data: dict[str, Any]) -> dict[str, Any]:
        """Insert or update on unique website_url conflict."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"%({k})s" for k in data.keys())
        update_set = ", ".join(
            f"{k} = EXCLUDED.{k}"
            for k in data.keys()
            if k != "website_url"
        )
        sql = (
            f"INSERT INTO {TABLE} ({columns}) VALUES ({placeholders}) "
            f"ON CONFLICT (website_url) DO UPDATE SET {update_set} "
            "RETURNING *"
        )
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, data)
                return dict(cur.fetchone())
