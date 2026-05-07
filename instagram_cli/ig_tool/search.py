"""Cache-aware orchestration over IGClient."""
from __future__ import annotations

import logging

from .cache import Cache
from .client import IGClient
from .models import Profile, UserSummary

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, client: IGClient, cache: Cache):
        self.client = client
        self.cache = cache

    def search(
        self,
        keyword: str,
        limit: int = 20,
        *,
        force_refresh: bool = False,
    ) -> list[UserSummary]:
        if not force_refresh:
            cached = self.cache.get_search(keyword)
            if cached is not None:
                logger.info("Cache hit for search %r (%d users)", keyword, len(cached))
                return cached[:limit]

        logger.info("Cache miss for search %r — calling Instagram", keyword)
        users = self.client.search_users(keyword, limit=limit)
        self.cache.put_search(keyword, users)
        return users

    def profile(self, username: str, *, force_refresh: bool = False) -> Profile:
        if not force_refresh:
            cached = self.cache.get_profile(username)
            if cached is not None:
                logger.info("Cache hit for profile %r", username)
                return cached

        logger.info("Cache miss for profile %r — calling Instagram", username)
        prof = self.client.fetch_profile(username)
        self.cache.put_profile(prof)
        return prof
