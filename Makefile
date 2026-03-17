.PHONY: web api test lint fmt migrate

web:
	cd apps/web && pnpm dev

api:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd apps/api && pytest -q

lint:
	cd apps/api && ruff check .
	cd apps/web && pnpm lint

fmt:
	cd apps/api && ruff format .
	cd apps/web && pnpm format

migrate:
	cd apps/api && alembic upgrade head
