"""Instagram tab for the Fetchster Streamlit app.

Wraps `instagram_cli.ig_tool` for in-browser use: collects IG credentials
through a Streamlit form, persists the instagrapi session per-user under
`instagram_cli/data/`, and exposes search + profile lookup. There is no
need to set IG creds in `.env` — they are entered in the UI.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from instagram_cli.ig_tool.cache import Cache
from instagram_cli.ig_tool.client import IGClient, IGClientError
from instagram_cli.ig_tool.config import Settings
from instagram_cli.ig_tool.search import SearchService

DATA_DIR = Path(__file__).resolve().parent / "instagram_cli" / "data"


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
        cache_ttl_seconds=7 * 24 * 3600,
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
        "or business account you care about. Credentials are kept in this "
        "browser session only; the IG session token is cached on disk so you "
        "don't have to re-authenticate every time."
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
        except Exception as exc:  # noqa: BLE001 — surface unexpected failures to the user
            st.error(f"Unexpected error: {exc}")
            return

    st.session_state.ig_client = client
    st.session_state.ig_cache = Cache(settings.db_path, settings.cache_ttl_seconds)
    st.session_state.ig_settings = settings
    st.session_state.ig_authenticated = True
    st.success("Logged in.")
    st.rerun()


def _logout() -> None:
    for key in ("ig_client", "ig_cache", "ig_settings", "ig_authenticated"):
        st.session_state.pop(key, None)


def _show_ig_search() -> None:
    settings: Settings = st.session_state.ig_settings
    client: IGClient = st.session_state.ig_client
    cache: Cache = st.session_state.ig_cache
    service = SearchService(client, cache)

    header_col, logout_col = st.columns([5, 1])
    with header_col:
        st.markdown(f"### Instagram — signed in as **{settings.ig_username}**")
        st.caption(
            f"Request cap: {settings.request_cap_per_session} per session · "
            f"delay {settings.request_delay_min:.0f}–{settings.request_delay_max:.0f}s · "
            f"cache TTL {settings.cache_ttl_seconds // 3600}h"
        )
    with logout_col:
        if st.button("Logout", use_container_width=True, key="ig_logout"):
            _logout()
            st.rerun()

    sub_search, sub_profile = st.tabs(["Search by keyword", "Profile lookup"])

    with sub_search:
        _render_keyword_search(service)

    with sub_profile:
        _render_profile_lookup(service)


def _render_keyword_search(service: SearchService) -> None:
    keyword = st.text_input("Keyword", key="ig_search_keyword", placeholder="e.g. coworking austin")
    limit = st.slider("Max results", 5, 50, 20, key="ig_search_limit")
    force = st.checkbox("Force refresh (bypass cache)", key="ig_search_force")

    if not st.button("Search", key="ig_search_btn", type="primary"):
        return
    if not keyword:
        st.warning("Enter a keyword first.")
        return

    with st.spinner("Searching Instagram..."):
        try:
            users = service.search(keyword, limit=limit, force_refresh=force)
        except IGClientError as exc:
            st.error(str(exc))
            return

    if not users:
        st.info("No results.")
        return

    df = pd.DataFrame([u.to_dict() for u in users])
    st.dataframe(df, use_container_width=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv_bytes,
        file_name=f"ig_search_{keyword.replace(' ', '_')}.csv",
        mime="text/csv",
        key="ig_search_download",
    )


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
        if profile.biography:
            st.markdown(profile.biography)
        if profile.external_url:
            st.markdown(f"[{profile.external_url}]({profile.external_url})")
        st.caption(f"Fetched {profile.fetched_at.isoformat(timespec='seconds')}")
