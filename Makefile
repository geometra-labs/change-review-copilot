.PHONY: web api worker test lint fmt migrate

web:
	cd apps/web && npm run dev

api:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd apps/api && python -m app.workers.run_worker

test:
	cd apps/api && pytest -q

lint:
	cd apps/api && ruff check .
	cd apps/web && npm run lint

fmt:
	cd apps/api && ruff format .
	cd apps/web && npm run format

migrate:
	cd apps/api && alembic upgrade head
