# Fetchster — Local setup & contribution guide

This is the onboarding doc for **Henry** to get Fetchster running on his own
machine, and the workflow for landing changes back on `main`. It's written so
each step can be copy-pasted into a terminal, and so Henry's Claude Code can
follow it end-to-end.

> Two ways to use the app:
>
> 1. **Just use it remotely** — open the live URL Julian shares (private ngrok
>    link, password-protected). No setup needed beyond knowing the password.
> 2. **Run it locally + contribute changes** — what the rest of this doc is
>    about.

---

## Prerequisites

- macOS or Linux
- Python 3.11 or newer (`python3 --version`)
- `git`
- (Optional, for the Instagram tab) a **throwaway** Instagram account — never
  a personal or business one. Using `instagrapi` violates IG's Terms of Use
  and the account you sign in with can be banned.

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/juliancoworkly/Fetchster.git ~/Fetchster
cd ~/Fetchster
```

The repo is private. If `git clone` fails with `Repository not found`, ask
Julian to confirm you've been added as a collaborator on GitHub (Settings →
Collaborators) and that you're authenticated to GitHub locally
(`gh auth status` or have an SSH key set up).

## Step 2 — Create the venv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

`pip install -e .` reads `pyproject.toml` and installs every Python dep
(streamlit, psycopg2, instagrapi, etc.). Takes 5–10 minutes the first time.

## Step 3 — Set up `.env`

```bash
cp .env.example .env
```

Open `.env` (it's hidden — `Cmd+Shift+.` in Finder, or just edit in your
terminal) and fill in **two** values. Get them from Julian via a secure
channel (Signal, 1Password, etc.), **not** email or any logged chat:

```env
DATABASE_URL=<paste from Julian — Neon Postgres connection string>
FETCHSTER_PASSWORD=<the shared site password>
```

Leave `SUPABASE_URL`, `SUPABASE_KEY`, and the Stripe keys blank — they're
only used for the payment flows that aren't wired up internally.

The DB is shared with Julian's instance, so any searches you save here will
also be visible to him (and vice versa). That's intentional — internal team
DB.

## Step 4 — Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501. You should see:

1. The Fetchster password page — enter `FETCHSTER_PASSWORD`
2. Two tabs: **Google (email harvesting)** and **Instagram**

For the Instagram tab, you log in with your throwaway IG creds **inside the
UI** — no `.env` configuration needed. The IG session token is cached at
`instagram_cli/data/session_<your_username>.json` so you don't have to
re-authenticate every run.

To stop the app: `Ctrl+C` in the terminal.

---

## Step 5 — Contribution workflow

**We don't push directly to `main`.** The flow is:
`feature branch → push → pull request → merge into main`.

```bash
# Make sure your local main is current
git checkout main
git pull origin main

# Create a feature branch — name it after the change
git checkout -b feature/short-description-of-change

# ... edit files ...

# Stage and commit. Be specific in the message.
git add <changed-files>
git commit -m "What this changes and why"

# Push the branch
git push -u origin feature/short-description-of-change
```

Then open a pull request:

```bash
gh pr create --title "Short title" --body "Longer description"
```

Or do it through GitHub's web UI. Tag Julian for review.

Once the PR is approved and merged on GitHub, clean up locally:

```bash
git checkout main
git pull origin main
git branch -d feature/short-description-of-change
```

**What not to do:**

- Don't `git push origin main` directly.
- Don't force-push (`git push --force`) anything you've shared.
- Don't commit `.env`, `instagram_cli/data/`, `.venv/`, or `__pycache__/`
  — they're already in `.gitignore` but worth knowing.

---

## Key files to know

| File | What it is |
|---|---|
| [app.py](app.py) | Main Streamlit entry. Site password gate, Google/Instagram tabs. |
| [instagram_module.py](instagram_module.py) | Instagram tab UI for Streamlit. Login form + search + profile lookup. |
| [instagram_cli/ig_tool/](instagram_cli/ig_tool/) | Instagram client wrapper (instagrapi + SQLite cache + per-session request cap). Used by both the standalone CLI and the Streamlit tab. |
| [instagram_cli/README.md](instagram_cli/README.md) | Standalone CLI usage and the full Instagram ToS warning. |
| [auth.py](auth.py) | Original login plumbing. The login UI is removed in internal mode, but downstream helpers (`is_authenticated`, `save_search_history`, etc.) are still called by the rest of the app. |
| [db/schema.sql](db/schema.sql) | Postgres schema. Already provisioned on the shared DB; reference only. |
| [pyproject.toml](pyproject.toml) | Python dependencies. |
| [.env.example](.env.example) | What env vars to set. |
| [.gitignore](.gitignore) | What's never committed. |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'instagram_cli.ig_tool'`**
Run `pip install -e .` from the repo root and confirm your venv is active
(`which python` should point to `~/Fetchster/.venv/bin/python`).

**`Database connection failed` on app startup**
`DATABASE_URL` is missing or wrong. Re-check `.env`. If it looks right and
you still can't connect, ask Julian to confirm the Neon hostname is current.

**Instagram tab → `Login challenge required`**
Instagram flagged the login. Open the IG app on your phone, resolve the
challenge prompt manually, then retry the login in Fetchster. Recurring
challenges = consider rotating to a different throwaway account.

**Instagram tab → `Rate-limited by Instagram`**
You hit the 50-request-per-session cap or IG itself is throttling. Restart
the app (cap resets), wait an hour or so, and use the cache rather than
forcing refresh.

**Streamlit hangs or shows stale code after editing a file**
Press `R` in the browser tab to rerun. If that doesn't pick up changes,
restart `streamlit run app.py`.

---

## Heads up

- The Google search tab uses the search API key stored per-user in the
  `user_profiles` table. If your account doesn't have one set, you'll need
  to add it via the existing Account flow (re-enabled by setting your
  Streamlit session manually) or ask Julian to provision one.
- The Instagram features hit `instagrapi`, which violates Instagram's ToS.
  Bans of the IG account you log in with are a realistic risk — see
  `instagram_cli/README.md` for details.
- This tool is **internal**. Don't share the live URL or password publicly.

---

## Quick reference

```bash
# Everyday loop
cd ~/Fetchster
source .venv/bin/activate
git checkout -b feature/foo
# edit, edit
git add -A && git commit -m "..."
git push -u origin feature/foo
gh pr create

# Run locally
streamlit run app.py
# → http://localhost:8501

# Update local main after a PR is merged
git checkout main
git pull origin main
```
