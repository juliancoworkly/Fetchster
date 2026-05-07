"""SQLite cache for search results and profiles, with TTL."""
from __future__ import annotations

import json
import logging
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .models import Profile, UserSummary

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    pk         TEXT PRIMARY KEY,
    username   TEXT NOT NULL,
    payload    TEXT NOT NULL,
    fetched_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username);

CREATE TABLE IF NOT EXISTS searches (
    keyword    TEXT NOT NULL,
    pk         TEXT NOT NULL,
    rank       INTEGER NOT NULL,
    payload    TEXT NOT NULL,
    fetched_at INTEGER NOT NULL,
    PRIMARY KEY (keyword, pk)
);
CREATE INDEX IF NOT EXISTS idx_searches_keyword ON searches(keyword, fetched_at);
"""


class Cache:
    """Tiny SQLite-backed cache for search results and profiles.

    Entries older than `ttl_seconds` are treated as misses.
    """

    def __init__(self, db_path: Path, ttl_seconds: int):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _is_fresh(self, fetched_at: int) -> bool:
        return (time.time() - fetched_at) < self.ttl_seconds

    @staticmethod
    def _normalize(keyword: str) -> str:
        return keyword.strip().lower()

    def get_profile(self, username: str) -> Profile | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload, fetched_at FROM profiles WHERE username = ?",
                (username,),
            ).fetchone()
        if not row:
            return None
        payload, fetched_at = row
        if not self._is_fresh(fetched_at):
            logger.debug("Cache expired for profile %s", username)
            return None
        return Profile.from_dict(json.loads(payload))

    def put_profile(self, profile: Profile) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO profiles (pk, username, payload, fetched_at) "
                "VALUES (?, ?, ?, ?)",
                (
                    profile.pk,
                    profile.username,
                    json.dumps(profile.to_dict()),
                    int(time.time()),
                ),
            )

    def get_search(self, keyword: str) -> list[UserSummary] | None:
        kw = self._normalize(keyword)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload, fetched_at FROM searches "
                "WHERE keyword = ? ORDER BY rank ASC",
                (kw,),
            ).fetchall()
        if not rows:
            return None
        if not all(self._is_fresh(r[1]) for r in rows):
            logger.debug("Cache expired for search %s", kw)
            return None
        return [UserSummary(**json.loads(r[0])) for r in rows]

    def put_search(self, keyword: str, users: list[UserSummary]) -> None:
        kw = self._normalize(keyword)
        now = int(time.time())
        with self._connect() as conn:
            conn.execute("DELETE FROM searches WHERE keyword = ?", (kw,))
            conn.executemany(
                "INSERT INTO searches (keyword, pk, rank, payload, fetched_at) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (kw, u.pk, i, json.dumps(u.to_dict()), now)
                    for i, u in enumerate(users)
                ],
            )
