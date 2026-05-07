# ig_tool

A small Python CLI for searching Instagram users by keyword and fetching public
profile data, with local SQLite caching. Built for personal, low-volume use.

---

## WARNING — read before using

This tool uses [`instagrapi`](https://github.com/subzeroid/instagrapi), which
talks to Instagram's **private mobile API**. That violates the
[Instagram Terms of Use](https://help.instagram.com/581066165581870), which
prohibit automated access without written permission.

Realistic risks:

- **Permanent ban** of the Instagram account whose credentials you use.
- **IP-level rate limits or blocks** that affect every account on your network.
- **Login challenges and 2FA loops** that can lock you out for hours or days.
- **Shadow-bans** where requests succeed but return empty or stale data with no
  visible error.

**Use a throwaway account.** Never log in with your primary or business
account. The tool ships with a 50-request-per-session cap, randomized 3–7
second delays between requests, and a 7-day result cache to keep call volume
low — but **none of these prevent a ban**.

If you need Instagram data for production or commercial use, use the official
[Instagram Graph API](https://developers.facebook.com/docs/instagram) instead.

You are responsible for how you use this tool. The author makes no warranty
and accepts no liability.

---

## Setup

Requires Python 3.11+.

```bash
cd instagram_cli
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and fill in IG_USERNAME and IG_PASSWORD
```

### `.env` example

```env
IG_USERNAME=your_throwaway_username
IG_PASSWORD=your_throwaway_password

# Optional — defaults shown
IG_SESSION_PATH=data/session.json
IG_DB_PATH=data/ig_cache.sqlite
IG_CACHE_TTL_SECONDS=604800       # 7 days
IG_DELAY_MIN=3
IG_DELAY_MAX=7
IG_REQUEST_CAP=50
IG_LOG_LEVEL=INFO
```

The first run logs in with username + password and writes `data/session.json`.
Subsequent runs reuse that session file and skip a fresh login.

---

## Usage

Invoke the tool as a Python module:

```bash
python -m ig_tool <command> [options]
```

### Search

```bash
python -m ig_tool search "rock climbing" --limit 25
```

Returns a table of usernames, full names, and verified/private flags. Results
are cached for 7 days; pass `--force-refresh` to bypass the cache.

### Profile

```bash
python -m ig_tool profile someusername
```

Returns the full public profile: bio, follower / following / post counts,
verified, private, business category, external URL.

### Export

```bash
python -m ig_tool export "rock climbing" --format csv --out climbers.csv
python -m ig_tool export "rock climbing" --format json --out climbers.json
```

Omit `--out` to write to stdout.

### Global options

| Option           | Description                                   |
|------------------|-----------------------------------------------|
| `--request-cap`  | Override the 50-request-per-session hard cap. |
| `--log-level`    | `DEBUG`, `INFO`, `WARNING`, `ERROR`.          |

Example:

```bash
python -m ig_tool --log-level DEBUG --request-cap 20 search nature
```

---

## How caching works

Search results and profiles are stored in `data/ig_cache.sqlite`. Entries
older than `IG_CACHE_TTL_SECONDS` (default 7 days) are treated as misses and
re-fetched on the next call. Delete the SQLite file to wipe the cache.

## How the request cap works

Every call to `search_users` or `user_info_by_username` increments a
per-process counter. When it hits `IG_REQUEST_CAP` (default 50), the next
call raises and the CLI exits with code `2`. This is a soft safeguard; it
resets when the process exits. Login validation requests do not count.

## Files written

| File                  | What it is                          | In `.gitignore`? |
|-----------------------|-------------------------------------|------------------|
| `.env`                | Your IG credentials.                | yes              |
| `data/session.json`   | Persisted instagrapi session.       | yes              |
| `data/ig_cache.sqlite`| SQLite cache for searches/profiles. | yes              |

---

## Project layout

```
instagram_cli/
  ig_tool/
    __init__.py
    __main__.py        # enables `python -m ig_tool`
    cli.py             # click entry point
    client.py          # instagrapi wrapper, session, throttling, request cap
    search.py          # cache-aware search & profile orchestration
    cache.py           # SQLite layer with TTL
    models.py          # UserSummary, Profile dataclasses
    config.py          # settings loaded from .env
  .env.example
  .gitignore
  README.md
  requirements.txt
```

## Exit codes

| Code | Meaning                                                        |
|------|----------------------------------------------------------------|
| 0    | Success.                                                       |
| 1    | Client error (login failed, challenge, rate limit, etc.).      |
| 2    | Request cap reached.                                           |
