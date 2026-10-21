import psycopg
import pytest
from faker import Faker

from repopulse.config import load_db_settings
from repopulse.simulator import actions
from repopulse.simulator.run import ACTIONS


def test_deletes_are_rarer_than_creates():
    weights = {func.__name__: weight for func, weight in ACTIONS}
    assert weights["delete_user"] < weights["create_user"]
    assert all(weight > 0 for weight in weights.values())


@pytest.fixture
def conn():
    try:
        connection = psycopg.connect(load_db_settings().dsn, connect_timeout=3)
    except psycopg.OperationalError:
        pytest.skip("local Postgres is not running (make db-up)")
    yield connection
    connection.close()


@pytest.mark.integration
def test_every_action_runs_and_reports(conn):
    fake = Faker()
    actions.seed_repos(conn, fake)
    for func, _ in ACTIONS:
        assert isinstance(func(conn, fake), str)


@pytest.mark.integration
def test_deleting_a_user_cascades_to_watchlist(conn):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (email, full_name) VALUES (%s, %s) RETURNING user_id",
            ("cascade-test@example.com", "Cascade Test"),
        )
        user_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO repos (repo_id, full_name) VALUES (999999, 'test/cascade') "
            "ON CONFLICT DO NOTHING"
        )
        cur.execute(
            "INSERT INTO watchlist_items (user_id, repo_id) VALUES (%s, 999999)",
            (user_id,),
        )
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        cur.execute(
            "SELECT count(*) FROM watchlist_items WHERE user_id = %s", (user_id,)
        )
        assert cur.fetchone()[0] == 0
    conn.commit()
