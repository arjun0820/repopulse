.PHONY: test lint fmt

test:
	uv run pytest

lint:
	uv run ruff check .

fmt:
	uv run ruff format .

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

db-reset:
	docker compose down -v
	docker compose up -d postgres

db-psql:
	docker compose exec postgres sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'