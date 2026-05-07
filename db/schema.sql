-- Fetchster Supabase schema
-- Run once in Supabase: SQL Editor → New query → paste this → Run.
-- Re-runnable: every CREATE uses IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS user_profiles (
    id                       SERIAL PRIMARY KEY,
    email                    TEXT NOT NULL UNIQUE,
    password_hash            TEXT NOT NULL,
    full_name                TEXT NOT NULL DEFAULT '',
    subscription_type        TEXT NOT NULL DEFAULT 'trial',
    subscription_status      TEXT NOT NULL DEFAULT 'trial',
    subscription_expires_at  TIMESTAMPTZ,
    searches_remaining       INTEGER NOT NULL DEFAULT 3,
    total_searches           INTEGER NOT NULL DEFAULT 0,
    api_key_encrypted        TEXT,
    login_token              TEXT,
    login_token_expires      TIMESTAMPTZ,
    stripe_customer_id       TEXT,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_stripe_customer ON user_profiles(stripe_customer_id);

CREATE TABLE IF NOT EXISTS user_keywords (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    keyword     TEXT NOT NULL,
    is_recent   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_keywords_user ON user_keywords(user_id);

CREATE TABLE IF NOT EXISTS search_history (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    keyword         TEXT NOT NULL,
    location        TEXT,
    results_count   INTEGER NOT NULL DEFAULT 0,
    results_data    JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_search_history_user_created
    ON search_history(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS activation_keys (
    id          SERIAL PRIMARY KEY,
    key         TEXT NOT NULL UNIQUE,
    used        BOOLEAN NOT NULL DEFAULT FALSE,
    used_by     INTEGER REFERENCES user_profiles(id) ON DELETE SET NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
