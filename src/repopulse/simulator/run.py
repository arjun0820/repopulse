import argparse
import random
import time

import psycopg
from faker import Faker

from repopulse.config import load_db_settings
from repopulse.simulator import actions

# (action, weight): mostly new activity, some edits, few deletions
ACTIONS = [
    (actions.create_user, 25),
    (actions.add_to_watchlist, 25),
    (actions.create_alert_rule, 15),
    (actions.change_plan, 12),
    (actions.toggle_rule, 10),
    (actions.remove_from_watchlist, 8),
    (actions.delete_user, 5),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate app activity in Postgres")
    parser.add_argument(
        "--events", type=int, default=100, help="how many actions to run"
    )
    parser.add_argument(
        "--delay", type=float, default=0.2, help="seconds between actions"
    )
    parser.add_argument("--seed", type=int, default=None, help="make a run repeatable")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        Faker.seed(args.seed)
    fake = Faker()

    funcs, weights = zip(*ACTIONS)
    settings = load_db_settings()
    try:
        with psycopg.connect(settings.dsn) as conn:
            actions.seed_repos(conn, fake)
            for i in range(1, args.events + 1):
                func = random.choices(funcs, weights=weights)[0]
                print(f"[{i}/{args.events}] {func.__name__}: {func(conn, fake)}")
                time.sleep(args.delay)
    except KeyboardInterrupt:
        print("\nstopped by user")


if __name__ == "__main__":
    main()
