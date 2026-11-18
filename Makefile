# Short commands for the development stack.
# Each one is a single docker compose line, so it also works by hand.
# More commands (tests, linting, migrations) arrive with later iterations.

.PHONY: up down logs psql shell

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
