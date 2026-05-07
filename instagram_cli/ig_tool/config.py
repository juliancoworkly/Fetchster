"""Settings loaded from environment / .env."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR: Path = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class Settings:
    ig_username: str
    ig_password: str
    session_path: Path
    db_path: Path
    cache_ttl_seconds: int
    request_delay_min: float
    request_delay_max: float
    request_cap_per_session: int
    log_level: str


def _required(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(
            f"Missing required env var: {key}. Copy .env.example to .env and fill it in."
        )
    return val


def _path(key: str, default: Path) -> Path:
    raw = os.getenv(key)
    return Path(raw) if raw else default


def load_settings() -> Settings:
    """Load Settings from environment variables. Raises if creds are missing."""
    DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    settings = Settings(
        ig_username=_required("IG_USERNAME"),
        ig_password=_required("IG_PASSWORD"),
        session_path=_path("IG_SESSION_PATH", DEFAULT_DATA_DIR / "session.json"),
        db_path=_path("IG_DB_PATH", DEFAULT_DATA_DIR / "ig_cache.sqlite"),
        cache_ttl_seconds=int(os.getenv("IG_CACHE_TTL_SECONDS", str(7 * 24 * 3600))),
        request_delay_min=float(os.getenv("IG_DELAY_MIN", "3.0")),
        request_delay_max=float(os.getenv("IG_DELAY_MAX", "7.0")),
        request_cap_per_session=int(os.getenv("IG_REQUEST_CAP", "50")),
        log_level=os.getenv("IG_LOG_LEVEL", "INFO"),
    )

    if settings.request_delay_min < 0 or settings.request_delay_max < settings.request_delay_min:
        raise RuntimeError(
            f"Invalid delay range: {settings.request_delay_min}..{settings.request_delay_max}"
        )
    if settings.request_cap_per_session <= 0:
        raise RuntimeError(f"IG_REQUEST_CAP must be positive (got {settings.request_cap_per_session})")

    return settings
