# Short commands for the development stack.
# Each one is a single docker compose line, so it also works by hand.
# More commands (migrations, the worker, seed data) arrive with later iterations.

.PHONY: up down logs psql shell lint test test-backend test-frontend

# Start the database, the backend and the frontend in the background.
up:
	docker compose up -d --build

# Stop everything. The database keeps its files.
down:
	docker compose down

# Follow what all three services are printing. Press Ctrl+C to stop watching.
logs:
	docker compose logs -f

# Open a database prompt inside the db container.
psql:
	docker compose exec db psql -U $${POSTGRES_USER:-classcraft} -d $${POSTGRES_DB:-classcraft}

# Open a shell inside the backend container.
shell:
	docker compose exec backend sh

# Read both languages for style mistakes and likely bugs, without running them.
# --no-deps keeps the database out of it; linting does not need one.
lint:
	docker compose run --rm --no-deps backend ruff check .
	docker compose run --rm --no-deps backend ruff format --check .
	docker compose run --rm --no-deps frontend npm run lint

# Everything the checks on GitHub run, except the slow solver tests.
test: test-backend test-frontend

# The backend tests talk to a real database, so this one starts the db first.
test-backend:
	docker compose run --rm backend pytest -m "not slow"

test-frontend:
	docker compose run --rm --no-deps frontend npm test
