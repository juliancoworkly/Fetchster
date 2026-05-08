"""Postgres-backed cache for IG searches and profiles.

Mirrors the API of `instagram_cli.ig_tool.cache.Cache` (SQLite) but persists
in the shared Postgres DB so cached entries survive Cloud Run container
restarts. No TTL by default — entries live until cleared explicitly.
"""
from __future__ import annotations

import json
import logging
from typing import Callable

import psycopg2.extras

from .models import Profile, UserSummary

logger = logging.getLogger(__name__)


class PgCache:
    """Postgres-backed cache. `connection_factory` returns a live connection
    on every call (delegated to `auth.init_database` so we share the cached
    Streamlit connection)."""

    def __init__(self, connection_factory: Callable[[], object]):
        self._get_conn = connection_factory

    @staticmethod
    def _normalize(keyword: str) -> str:
        return keyword.strip().lower()

    def get_profile(self, username: str) -> Profile | None:
        conn = self._get_conn()
        if conn is None:
            return None
        with conn.cursor() as cur:
            cur.execute(
                "SELECT payload FROM ig_profile_cache WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
        if not row:
            return None
        payload = row[0]
        if isinstance(payload, str):
            payload = json.loads(payload)
        return Profile.from_dict(payload)

    def put_profile(self, profile: Profile) -> None:
        conn = self._get_conn()
        if conn is None:
            return
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ig_profile_cache (username, payload, fetched_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (username) DO UPDATE
                    SET payload = EXCLUDED.payload, fetched_at = NOW()
                """,
                (profile.username, json.dumps(profile.to_dict())),
            )

    def get_search(self, keyword: str) -> list[UserSummary] | None:
        kw = self._normalize(keyword)
        conn = self._get_conn()
        if conn is None:
            return None
        with conn.cursor() as cur:
            cur.execute(
                "SELECT payload FROM ig_search_cache WHERE keyword = %s ORDER BY rank ASC",
                (kw,),
            )
            rows = cur.fetchall()
        if not rows:
            return None
        out: list[UserSummary] = []
        for row in rows:
            payload = row[0]
            if isinstance(payload, str):
                payload = json.loads(payload)
            out.append(UserSummary(**payload))
        return out

    def put_search(self, keyword: str, users: list[UserSummary]) -> None:
        kw = self._normalize(keyword)
        conn = self._get_conn()
        if conn is None:
            return
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ig_search_cache WHERE keyword = %s", (kw,))
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO ig_search_cache (keyword, pk, rank, payload) VALUES %s",
                [
                    (kw, u.pk, i, json.dumps(u.to_dict()))
                    for i, u in enumerate(users)
                ],
            )

    def clear_searches(self) -> int:
        """Delete every cached keyword search. Returns rows deleted."""
        conn = self._get_conn()
        if conn is None:
            return 0
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ig_search_cache")
            return cur.rowcount or 0

    def clear_profiles(self) -> int:
        """Delete every cached profile. Returns rows deleted."""
        conn = self._get_conn()
        if conn is None:
            return 0
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ig_profile_cache")
            return cur.rowcount or 0

    def clear_search(self, keyword: str) -> int:
        kw = self._normalize(keyword)
        conn = self._get_conn()
        if conn is None:
            return 0
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ig_search_cache WHERE keyword = %s", (kw,))
            return cur.rowcount or 0

    def stats(self) -> dict[str, int]:
        conn = self._get_conn()
        if conn is None:
            return {"searches": 0, "profiles": 0}
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(DISTINCT keyword) FROM ig_search_cache")
            search_count = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM ig_profile_cache")
            profile_count = cur.fetchone()[0] or 0
        return {"searches": int(search_count), "profiles": int(profile_count)}
