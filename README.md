# Fetchster

Fetchster is a Streamlit email discovery app that uses Serper.dev for Google Search and Maps data, then scans business websites for contact emails.

## Local Setup

1. Create and activate a Python environment:

   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install -e .
   ```

2. Configure environment variables:

   ```bash
   cp .env.example .env
   ```

   At minimum, set `DATABASE_URL` to a PostgreSQL database. Users add their own Serper.dev API key inside the app after login.

3. Run the app:

   ```bash
   .venv/bin/streamlit run app.py --server.address 127.0.0.1 --server.port 5000
   ```

4. Open `http://127.0.0.1:5000`.

## Admin Bootstrap

Hardcoded admin passwords were removed. To create a first admin account, set:

```bash
FETCHSTER_BOOTSTRAP_ADMIN_EMAIL=admin@example.com
FETCHSTER_BOOTSTRAP_ADMIN_PASSWORD=change-me
FETCHSTER_ADMIN_EMAILS=admin@example.com
```

The account is created on the first successful database connection if it does not already exist.

You can also create or reset an admin account directly:

```bash
.venv/bin/python scripts/create_admin.py --email admin@fetchster.io --password "change-me"
```

## Required Services

- PostgreSQL via `DATABASE_URL`
- Stripe keys for paid subscription flows
- Optional Supabase keys for legacy subscription analytics
- Serper.dev API key, stored per user after login

## Cloud Run Deployment

Fetchster can run on Cloud Run with the included `Dockerfile`.

```bash
gcloud run deploy fetchster \
  --source . \
  --project coworkly-17cfa \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file cloudrun.env.yaml
```

For `fetchster.io`, verify the domain in Google first, then create mappings for the apex and `www` domains:

```bash
gcloud beta run domain-mappings create \
  --service fetchster \
  --domain fetchster.io \
  --region us-central1 \
  --project coworkly-17cfa

gcloud beta run domain-mappings create \
  --service fetchster \
  --domain www.fetchster.io \
  --region us-central1 \
  --project coworkly-17cfa
```

Google will return DNS records that must be added in GoDaddy, where `fetchster.io` currently uses `domaincontrol.com` nameservers.
