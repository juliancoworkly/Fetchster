"""instagrapi wrapper: session reuse, throttling, request cap, error handling."""
from __future__ import annotations

import logging
import random
import time
from typing import Any, Callable

from instagrapi import Client
from instagrapi.exceptions import (
    ChallengeRequired,
    ClientError,
    LoginRequired,
    PleaseWaitFewMinutes,
    RateLimitError,
)

from .config import Settings
from .models import Profile, UserSummary

logger = logging.getLogger(__name__)


class IGClientError(Exception):
    """Wrapper so callers don't need to import instagrapi exceptions."""


class RequestCapReached(IGClientError):
    """Raised when the per-session request cap is hit."""


class IGClient:
    """Thin wrapper around `instagrapi.Client` with session persistence,
    randomized delays, and a per-process request cap."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = Client()
        self._request_count = 0
        self._authenticated = False

    def login(self) -> None:
        """Reuse session from disk if possible, otherwise log in fresh."""
        session_path = self.settings.session_path

        if session_path.exists():
            try:
                self.client.load_settings(session_path)
                # `login` after `load_settings` validates the session; if it's
                # still good, no fresh login is performed.
                self.client.login(self.settings.ig_username, self.settings.ig_password)
                logger.info("Reused session from %s", session_path)
                self._authenticated = True
                return
            except (LoginRequired, ChallengeRequired, ClientError) as exc:
                logger.warning("Stored session invalid (%s); logging in fresh", exc)
                session_path.unlink(missing_ok=True)
                self.client = Client()  # reset to clear stale settings

        try:
            self.client.login(self.settings.ig_username, self.settings.ig_password)
        except ChallengeRequired as exc:
            logger.error(
                "Instagram requires a manual challenge for %s. "
                "Open the IG app, resolve it, then re-run.",
                self.settings.ig_username,
            )
            raise IGClientError("Login challenge required.") from exc
        except ClientError as exc:
            logger.error("Login failed: %s", exc)
            raise IGClientError(f"Login failed: {exc}") from exc

        session_path.parent.mkdir(parents=True, exist_ok=True)
        self.client.dump_settings(session_path)
        logger.info(
            "Logged in as %s; session saved to %s",
            self.settings.ig_username,
            session_path,
        )
        self._authenticated = True

    def _throttle(self) -> None:
        delay = random.uniform(
            self.settings.request_delay_min, self.settings.request_delay_max
        )
        logger.debug("Sleeping %.2fs", delay)
        time.sleep(delay)

    def _check_cap(self) -> None:
        if self._request_count >= self.settings.request_cap_per_session:
            raise RequestCapReached(
                f"Request cap of {self.settings.request_cap_per_session} reached "
                "this session. Re-run later or raise --request-cap."
            )

    def _call(self, label: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if not self._authenticated:
            raise IGClientError("Not authenticated; call login() first.")
        self._check_cap()
        self._request_count += 1
        logger.info(
            "API call: %s (%d/%d this session)",
            label,
            self._request_count,
            self.settings.request_cap_per_session,
        )
        try:
            result = fn(*args, **kwargs)
        except (RateLimitError, PleaseWaitFewMinutes) as exc:
            logger.error("Rate-limited on %s: %s", label, exc)
            raise IGClientError(f"Rate-limited by Instagram on {label}: {exc}") from exc
        except ChallengeRequired as exc:
            logger.error("Challenge required during %s: %s", label, exc)
            raise IGClientError(f"Challenge required during {label}: {exc}") from exc
        except LoginRequired as exc:
            logger.error("Session expired during %s: %s", label, exc)
            self.settings.session_path.unlink(missing_ok=True)
            raise IGClientError(
                "Session expired. Delete data/session.json and re-run to log in again."
            ) from exc
        except ClientError as exc:
            logger.error("Client error on %s: %s", label, exc)
            raise IGClientError(f"Client error on {label}: {exc}") from exc

        self._throttle()
        return result

    def search_users(self, keyword: str, limit: int = 20) -> list[UserSummary]:
        results = self._call("search_users", self.client.search_users, keyword, limit)
        return [
            UserSummary(
                pk=str(u.pk),
                username=u.username,
                full_name=u.full_name or "",
                is_private=bool(u.is_private),
                is_verified=bool(u.is_verified),
                profile_pic_url=str(u.profile_pic_url) if getattr(u, "profile_pic_url", None) else None,
            )
            for u in results[:limit]
        ]

    def fetch_profile(self, username: str) -> Profile:
        info = self._call(
            "user_info_by_username", self.client.user_info_by_username, username
        )
        return Profile(
            pk=str(info.pk),
            username=info.username,
            full_name=info.full_name or "",
            biography=info.biography or "",
            follower_count=int(info.follower_count or 0),
            following_count=int(info.following_count or 0),
            media_count=int(info.media_count or 0),
            is_private=bool(info.is_private),
            is_verified=bool(info.is_verified),
            is_business=bool(getattr(info, "is_business", False)),
            category=getattr(info, "category", None) or getattr(info, "category_name", None),
            external_url=str(info.external_url) if getattr(info, "external_url", None) else None,
            profile_pic_url=str(info.profile_pic_url) if getattr(info, "profile_pic_url", None) else None,
        )
