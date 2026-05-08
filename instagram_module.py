"""Instagram tab for the Fetchster Streamlit app.

Wraps `instagram_cli.ig_tool` for in-browser use:
- IG credentials entered through a Streamlit form (not .env)
- Search and profile results cached in Postgres so they persist across
  Cloud Run restarts and never auto-expire
- One-click email/contact enrichment that fetches each user's full profile
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st

from auth import init_database
from instagram_cli.ig_tool.client import IGClient, IGClientError
from instagram_cli.ig_tool.config import Settings
from instagram_cli.ig_tool.pg_cache import PgCache
from instagram_cli.ig_tool.search import SearchService

DATA_DIR = Path(__file__).resolve().parent / "instagram_cli" / "data"

# Effectively no expiry — entries persist until manually cleared.
CACHE_TTL_SECONDS = 100 * 365 * 24 * 3600

EMAIL_RE = re.compile(r"[\w.+\-]+@[\w-]+\.[\w.\-]+")


def show_instagram_interface() -> None:
    if not st.session_state.get("ig_authenticated"):
        _show_ig_login()
    else:
        _show_ig_search()


def _build_settings(username: str, password: str) -> Settings:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe_user = "".join(c for c in username if c.isalnum() or c in "._-") or "user"
    return Settings(
        ig_username=username,
        ig_password=password,
        session_path=DATA_DIR / f"session_{safe_user}.json",
        db_path=DATA_DIR / "ig_cache.sqlite",
        cache_ttl_seconds=CACHE_TTL_SECONDS,
        request_delay_min=3.0,
        request_delay_max=7.0,
        request_cap_per_session=50,
        log_level="INFO",
    )


def _show_ig_login() -> None:
    st.markdown("### Instagram login")
    st.warning(
        "**Use a throwaway Instagram account.** This tool talks to Instagram's "
        "private API via `instagrapi`, which violates IG's Terms of Use and can "
        "result in a ban of the account you sign in with. Don't use a personal "
        "or business account you care about. Credentials stay in this browser "
        "session only; the IG session token is cached on disk so you don't have "
        "to re-authenticate every time."
    )

    with st.form("ig_login_form"):
        username = st.text_input("IG Username")
        password = st.text_input("IG Password", type="password")
        submitted = st.form_submit_button("Login to Instagram", type="primary")

    if not submitted:
        return

    if not username or not password:
        st.error("Username and password are required.")
        return

    with st.spinner("Logging in to Instagram..."):
        try:
            settings = _build_settings(username.strip(), password)
            client = IGClient(settings)
            client.login()
        except IGClientError as exc:
            st.error(f"Login failed: {exc}")
            return
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unexpected error: {exc}")
            return

    st.session_state.ig_client = client
    st.session_state.ig_cache = PgCache(init_database)
    st.session_state.ig_settings = settings
    st.session_state.ig_authenticated = True
    st.success("Logged in.")
    st.rerun()


def _logout() -> None:
    for key in ("ig_client", "ig_cache", "ig_settings", "ig_authenticated"):
        st.session_state.pop(key, None)
    # Don't clear search-result session keys here; switching account keeps results.


def _show_ig_search() -> None:
    settings: Settings = st.session_state.ig_settings
    client: IGClient = st.session_state.ig_client
    cache: PgCache = st.session_state.ig_cache
    service = SearchService(client, cache)

    header_col, logout_col = st.columns([5, 1])
    with header_col:
        st.markdown(f"### Instagram — signed in as **{settings.ig_username}**")
        stats = cache.stats()
        st.caption(
            f"Cache: {stats['searches']} keyword searches · {stats['profiles']} profiles · "
            f"persistent · request cap {settings.request_cap_per_session}/session · "
            f"delay {settings.request_delay_min:.0f}–{settings.request_delay_max:.0f}s"
        )
    with logout_col:
        if st.button("Logout", use_container_width=True, key="ig_logout"):
            _logout()
            st.rerun()

    sub_search, sub_profile, sub_admin = st.tabs(
        ["Search by keyword", "Profile lookup", "Cache"]
    )

    with sub_search:
        _render_keyword_search(service, cache)

    with sub_profile:
        _render_profile_lookup(service)

    with sub_admin:
        _render_cache_admin(cache)


def _users_to_display_df(users: list, *, enrichment: dict[str, dict] | None = None) -> pd.DataFrame:
    """Build a 1-indexed DataFrame for display. Hides pk/profile_pic_url.

    If `enrichment` is provided, merges email/phone/bio columns from cached
    profiles keyed by username.
    """
    rows = []
    for u in users:
        row = {
            "Username": u.username,
            "Full name": u.full_name or "",
            "Verified": "yes" if u.is_verified else "",
            "Private": "yes" if u.is_private else "",
        }
        if enrichment is not None:
            extra = enrichment.get(u.username, {})
            row["Email"] = extra.get("email", "")
            row["Phone"] = extra.get("phone", "")
            row["Bio"] = extra.get("bio", "")
            row["External URL"] = extra.get("external_url", "")
        rows.append(row)
    df = pd.DataFrame(rows)
    df.index = range(1, len(df) + 1)
    df.index.name = "#"
    return df


def _extract_emails(*texts: str | None) -> list[str]:
    seen: list[str] = []
    for text in texts:
        if not text:
            continue
        for match in EMAIL_RE.findall(text):
            if match not in seen:
                seen.append(match)
    return seen


def _render_keyword_search(service: SearchService, cache: PgCache) -> None:
    keyword = st.text_input(
        "Keyword", key="ig_search_keyword", placeholder="e.g. coworking austin"
    )
    col_a, col_b, col_c = st.columns([2, 2, 1])
    with col_a:
        limit = st.slider("Max results", 5, 50, 20, key="ig_search_limit")
    with col_b:
        force = st.checkbox(
            "Force refresh (re-fetch from Instagram)", key="ig_search_force"
        )
    with col_c:
        st.write("")  # spacing
        run_search = st.button("Search", key="ig_search_btn", type="primary")

    if run_search and keyword:
        with st.spinner("Searching Instagram..."):
            try:
                users = service.search(keyword, limit=limit, force_refresh=force)
            except IGClientError as exc:
                st.error(str(exc))
                return
        st.session_state["ig_last_search_keyword"] = keyword
        st.session_state["ig_last_search_users"] = users
        # Drop any prior enrichment for the new search.
        st.session_state.pop("ig_last_enrichment", None)

    users = st.session_state.get("ig_last_search_users")
    keyword_shown = st.session_state.get("ig_last_search_keyword", "")
    if not users:
        st.info("Run a search to see results. Cached searches re-render instantly.")
        return

    enrichment = st.session_state.get("ig_last_enrichment")

    enrich_col, _ = st.columns([2, 5])
    with enrich_col:
        if st.button(
            "Enrich with emails / contact info",
            key="ig_enrich_btn",
            help="Fetches each user's full profile and pulls public_email, "
                 "phone, bio, and external URL. Counts toward the per-session "
                 "request cap. Cached profiles don't re-fetch.",
        ):
            enrichment = _run_enrichment(service, users)
            if enrichment is not None:
                st.session_state["ig_last_enrichment"] = enrichment

    df = _users_to_display_df(users, enrichment=enrichment)
    st.dataframe(df, use_container_width=True)

    csv_bytes = df.to_csv(index=True).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv_bytes,
        file_name=f"ig_search_{keyword_shown.replace(' ', '_') or 'results'}.csv",
        mime="text/csv",
        key="ig_search_download",
    )


def _run_enrichment(service: SearchService, users: list) -> dict[str, dict] | None:
    """Fetch each user's profile, extract emails / phone / bio. Cached entries
    are free; uncached ones cost one IG API call each."""
    progress = st.progress(0.0, text="Enriching...")
    out: dict[str, dict] = {}
    total = len(users)
    for i, u in enumerate(users):
        progress.progress((i + 1) / total, text=f"Enriching {i+1}/{total}: {u.username}")
        try:
            profile = service.profile(u.username)
        except IGClientError as exc:
            out[u.username] = {"email": f"(error: {exc})"}
            # Stop scanning further if we hit the request cap or rate limit.
            if "cap" in str(exc).lower() or "rate" in str(exc).lower():
                progress.empty()
                st.warning(f"Stopped enrichment at {i+1}/{total}: {exc}")
                return out
            continue
        emails = []
        if profile.public_email:
            emails.append(profile.public_email)
        emails += [e for e in _extract_emails(profile.biography) if e not in emails]
        out[u.username] = {
            "email": ", ".join(emails),
            "phone": profile.contact_phone or "",
            "bio": profile.biography or "",
            "external_url": profile.external_url or "",
        }
    progress.empty()
    st.success(f"Enriched {total} profiles.")
    return out


def _render_profile_lookup(service: SearchService) -> None:
    username = st.text_input("Username (without @)", key="ig_profile_username")
    force = st.checkbox("Force refresh (bypass cache)", key="ig_profile_force")
    if not st.button("Fetch profile", key="ig_profile_btn", type="primary"):
        return
    if not username:
        st.warning("Enter a username first.")
        return

    with st.spinner("Fetching profile..."):
        try:
            profile = service.profile(username.strip().lstrip("@"), force_refresh=force)
        except IGClientError as exc:
            st.error(str(exc))
            return

    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.metric("Followers", f"{profile.follower_count:,}")
        st.metric("Following", f"{profile.following_count:,}")
        st.metric("Posts", f"{profile.media_count:,}")
    with col_r:
        st.markdown(f"### @{profile.username}")
        if profile.full_name:
            st.markdown(f"**{profile.full_name}**")
        flags = []
        if profile.is_verified:
            flags.append("verified")
        if profile.is_private:
            flags.append("private")
        if profile.is_business:
            flags.append("business")
        if flags:
            st.caption(" · ".join(flags))
        if profile.category:
            st.caption(f"Category: {profile.category}")
        if profile.public_email:
            st.markdown(f"**Email:** {profile.public_email}")
        if profile.contact_phone:
            st.markdown(f"**Phone:** {profile.contact_phone}")
        if profile.biography:
            st.markdown(profile.biography)
        if profile.external_url:
            st.markdown(f"[{profile.external_url}]({profile.external_url})")
        st.caption(f"Fetched {profile.fetched_at.isoformat(timespec='seconds')}")


def _render_cache_admin(cache: PgCache) -> None:
    stats = cache.stats()
    st.markdown("### Cache")
    st.write(
        f"**{stats['searches']}** keyword searches and **{stats['profiles']}** "
        "profiles are stored. Entries do not auto-expire — clear them manually "
        "to force fresh fetches."
    )
    col_s, col_p = st.columns(2)
    with col_s:
        if st.button("Clear all keyword searches", key="ig_clear_searches"):
            n = cache.clear_searches()
            st.session_state.pop("ig_last_search_users", None)
            st.session_state.pop("ig_last_enrichment", None)
            st.success(f"Removed {n} cached search rows.")
            st.rerun()
    with col_p:
        if st.button("Clear all cached profiles", key="ig_clear_profiles"):
            n = cache.clear_profiles()
            st.session_state.pop("ig_last_enrichment", None)
            st.success(f"Removed {n} cached profile rows.")
            st.rerun()
