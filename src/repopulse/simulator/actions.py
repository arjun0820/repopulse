import random

import psycopg
from faker import Faker

PLANS = ["free", "pro", "team"]
METRICS = ["stars_per_hour", "open_issues", "first_response_hours"]
LANGUAGES = ["Python", "Go", "Rust", "TypeScript", "Java", "C++", "Ruby"]


def _run(conn: psycopg.Connection, sql: str, params: tuple = ()):
    """Run one statement as its own transaction and return the first row."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
    conn.commit()
    return row


def seed_repos(conn: psycopg.Connection, fake: Faker, count: int = 50) -> None:
    """Create a pool of repos if the table is empty. Safe to re-run."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM repos")
        if cur.fetchone()[0] > 0:
            return
        for i in range(1, count + 1):
            cur.execute(
                "INSERT INTO repos (repo_id, full_name, primary_language) "
                "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (
                    1000 + i,
                    f"{fake.user_name()}/{fake.slug()}",
                    random.choice(LANGUAGES),
                ),
            )
    conn.commit()


def create_user(conn: psycopg.Connection, fake: Faker) -> str:
    row = _run(
        conn,
        "INSERT INTO users (email, full_name, country) VALUES (%s, %s, %s) "
        "ON CONFLICT (email) DO NOTHING RETURNING user_id",
        (fake.email(), fake.name(), fake.country_code()),
    )
    return f"created user {row[0]}" if row else "skipped: email already exists"


def change_plan(conn: psycopg.Connection, fake: Faker) -> str:
    row = _run(
        conn,
        "UPDATE users SET plan = %s WHERE user_id = "
        "(SELECT user_id FROM users ORDER BY random() LIMIT 1) "
        "RETURNING user_id, plan",
        (random.choice(PLANS),),
    )
    return f"user {row[0]} now on plan {row[1]}" if row else "skipped: no users"


def add_to_watchlist(conn: psycopg.Connection, fake: Faker) -> str:
    row = _run(
        conn,
        "INSERT INTO watchlist_items (user_id, repo_id) "
        "SELECT u.user_id, r.repo_id "
        "FROM (SELECT user_id FROM users ORDER BY random() LIMIT 1) u, "
        "(SELECT repo_id FROM repos ORDER BY random() LIMIT 1) r "
        "ON CONFLICT DO NOTHING RETURNING user_id, repo_id",
    )
    return (
        f"user {row[0]} watches repo {row[1]}" if row else "skipped: already watching"
    )


def remove_from_watchlist(conn: psycopg.Connection, fake: Faker) -> str:
    row = _run(
        conn,
        "DELETE FROM watchlist_items WHERE (user_id, repo_id) = "
        "(SELECT user_id, repo_id FROM watchlist_items ORDER BY random() LIMIT 1) "
        "RETURNING user_id, repo_id",
    )
    return (
        f"user {row[0]} unwatched repo {row[1]}" if row else "skipped: empty watchlist"
    )


def create_alert_rule(conn: psycopg.Connection, fake: Faker) -> str:
    row = _run(
        conn,
        "INSERT INTO alert_rules (user_id, repo_id, metric, threshold) "
        "SELECT user_id, repo_id, %s::text, %s::numeric FROM watchlist_items "
        "ORDER BY random() LIMIT 1 RETURNING rule_id, user_id",
        (random.choice(METRICS), random.randint(1, 100)),
    )
    return (
        f"rule {row[0]} created for user {row[1]}" if row else "skipped: no watchlist"
    )


def toggle_rule(conn: psycopg.Connection, fake: Faker) -> str:
    row = _run(
        conn,
        "UPDATE alert_rules SET is_active = NOT is_active WHERE rule_id = "
        "(SELECT rule_id FROM alert_rules ORDER BY random() LIMIT 1) "
        "RETURNING rule_id, is_active",
    )
    return f"rule {row[0]} active={row[1]}" if row else "skipped: no rules"


def delete_user(conn: psycopg.Connection, fake: Faker) -> str:
    row = _run(
        conn,
        "DELETE FROM users WHERE user_id = "
        "(SELECT user_id FROM users ORDER BY random() LIMIT 1) RETURNING user_id",
    )
    return f"deleted user {row[0]}" if row else "skipped: no users"
