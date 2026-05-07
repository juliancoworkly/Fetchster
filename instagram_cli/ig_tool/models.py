"""Dataclasses for Instagram users and profiles."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class UserSummary:
    """Lightweight user record returned by `search_users`."""

    pk: str
    username: str
    full_name: str
    is_private: bool
    is_verified: bool
    profile_pic_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Profile:
    """Full public profile for a single user."""

    pk: str
    username: str
    full_name: str
    biography: str
    follower_count: int
    following_count: int
    media_count: int
    is_private: bool
    is_verified: bool
    is_business: bool
    category: str | None = None
    external_url: str | None = None
    profile_pic_url: str | None = None
    fetched_at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["fetched_at"] = self.fetched_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Profile":
        d = dict(data)
        if isinstance(d.get("fetched_at"), str):
            d["fetched_at"] = datetime.fromisoformat(d["fetched_at"])
        return cls(**d)
