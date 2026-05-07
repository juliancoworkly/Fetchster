"""Create or update a local Fetchster admin account."""

import argparse
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def parse_args():
    parser = argparse.ArgumentParser(description="Create or update a Fetchster admin user.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", default="Fetchster Admin")
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.database_url:
        raise SystemExit("DATABASE_URL is required.")

    from auth import ensure_database_schema, hash_password

    password_hash = hash_password(args.password)

    conn = psycopg2.connect(args.database_url)
    conn.autocommit = True
    ensure_database_schema(conn)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO user_profiles (
                email, password_hash, full_name, subscription_type,
                subscription_status, searches_remaining, total_searches
            )
            VALUES (%s, %s, %s, 'lifetime', 'active', 999999, 0)
            ON CONFLICT (email) DO UPDATE SET
                password_hash = EXCLUDED.password_hash,
                full_name = EXCLUDED.full_name,
                subscription_type = 'lifetime',
                subscription_status = 'active',
                searches_remaining = 999999,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, email, subscription_type, subscription_status
            """,
            (args.email, password_hash, args.name),
        )
        user = cursor.fetchone()

    conn.close()
    print(f"Admin ready: id={user[0]} email={user[1]} type={user[2]} status={user[3]}")


if __name__ == "__main__":
    main()
