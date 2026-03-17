# Change Review Copilot

Geometry-first CAD assembly change review.

## What It Does

Upload two versions of a mechanical assembly and receive a grounded report showing:

- what changed
- what parts are likely affected
- what risks to inspect
- what to inspect next

## Core Principle

Geometry first. Explanation second.

The system must compute structured findings before any language model is used.

## Stack

- Next.js
- FastAPI
- Postgres
- local file storage for bootstrap artifacts
- deterministic parse, diff, and impact logic
- LLM only for explanation

## Version Policy

This repo is set up to be predictable across Windows, macOS, and Linux.

- Python: `3.12.10`
- Node.js: `22.14.0`
- npm: `10.x`
- Docker Compose: v2+

Pinned helper files:

- Python: [/.python-version](/c:/Users/dipes/Documents/change-review/.python-version)
- Node: [/.nvmrc](/c:/Users/dipes/Documents/change-review/.nvmrc)

Backend Python compatibility is also enforced in [apps/api/pyproject.toml](/c:/Users/dipes/Documents/change-review/apps/api/pyproject.toml).

## Prerequisites

Install these first:

- `uv`
- Node.js `22.14.0`
- npm `10.x`
- Docker Desktop or Docker Engine with Compose

Recommended installers:

- `uv`: https://docs.astral.sh/uv/getting-started/installation/
- Node.js `22`: https://nodejs.org/

## Repo Setup

### 1. Clone and enter the repo

```bash
git clone <your-repo-url>
cd change-review
```

### 2. Create your local env file

Use the root example as the working env file:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Windows Git Bash / macOS / Linux:

```bash
cp .env.example .env
```

### 3. Create the Python environment with `uv`

This project currently uses a repo-local virtual environment named `.change-review`.

Install the pinned Python version:

```bash
uv python install 3.12.10
```

Create the virtual environment:

```bash
uv venv .change-review --python 3.12.10
```

Activate it:

Windows PowerShell:

```powershell
.\.change-review\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.\.change-review\Scripts\activate.bat
```

Windows Git Bash:

```bash
source .change-review/Scripts/activate
```

macOS / Linux:

```bash
source .change-review/bin/activate
```

Install backend dependencies from the API project with `uv`:

```bash
uv pip install -e ./apps/api
```

Why this shape:

- `uv` manages Python and the virtualenv consistently
- the environment lives at repo root, which keeps Windows and Git Bash commands simple
- `-e ./apps/api` installs the actual FastAPI project and its pinned dependencies

### 4. Install frontend dependencies

```bash
cd apps/web
npm install
cd ../..
```

If you use `nvm`, make sure you switch to the pinned Node version first:

```bash
nvm use
```

## First-Time Bootstrap

### 1. Start Postgres

```bash
docker compose up -d db
```

### 2. Run database migrations

If your Python environment is activated:

```bash
cd apps/api
alembic upgrade head
cd ../..
```

If you prefer explicit Python invocation:

Windows:

```powershell
.\.change-review\Scripts\python -m alembic -c apps/api/alembic.ini upgrade head
```

macOS / Linux:

```bash
./.change-review/bin/python -m alembic -c apps/api/alembic.ini upgrade head
```

### 3. Seed demo data

```bash
python scripts/seed_demo_data.py
```

Expected seeded user:

- email: `demo@example.com`
- password: `password123`

## Running The App

### Backend

If `make` is available:

```bash
make api
```

If `make` is not available, use the repo launcher:

Windows:

```bash
./dev.cmd api
```

macOS / Linux:

```bash
cd apps/api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

If `make` is available:

```bash
make web
```

If `make` is not available:

Windows:

```bash
./dev.cmd web
```

macOS / Linux:

```bash
cd apps/web
npm run dev
```

## Browser Flow

Once both servers are running:

1. Open `http://localhost:3000/login`
2. Log in with `demo@example.com` / `password123`
3. Open `/projects`
4. Create a project or use an existing one
5. Upload:
   - [demo_before.json](/c:/Users/dipes/Documents/change-review/data/fixtures/demo_before.json)
   - [demo_after.json](/c:/Users/dipes/Documents/change-review/data/fixtures/demo_after.json)
6. Wait for parse + compare
7. Open the comparison report
8. Export the JSON report

## Useful Commands

### Backend checks

```bash
cd apps/api
python -m compileall app
python -m pytest -q
```

### Migrations

```bash
cd apps/api
alembic upgrade head
```

### Seed data

```bash
python scripts/seed_demo_data.py
```

### Smoke test

```bash
bash scripts/smoke_test.sh
```

## Windows Notes

- If `make` is not installed, use [dev.cmd](/c:/Users/dipes/Documents/change-review/dev.cmd).
- If `pnpm` is not installed, the Windows launcher automatically falls back to `npm`.
- Use `source .change-review/Scripts/activate` in Git Bash, not the PowerShell activation command.
- If PowerShell blocks script activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Current Scope

This setup supports the bootstrap flow that exists today:

- auth
- projects
- upload of normalized JSON fixtures
- parse persistence
- comparison creation
- persisted impact findings
- report export

## Not Stable Yet

This is still an internal prototype. The following areas are intentionally not fully hardened yet:

- async job orchestration
- CAD-native ingestion
- frontend route guards
- richer project history/status polling
- PDF export
- full DB-backed integration tests

## Troubleshooting

### `alembic` cannot find settings

Make sure `.env` exists at repo root and your virtualenv is activated.

### `python scripts/seed_demo_data.py` fails on imports

Make sure you installed backend deps with:

```bash
uv pip install -e ./apps/api
```

### `npm install` fails on version conflicts

Use Node `22.14.0` from [/.nvmrc](/c:/Users/dipes/Documents/change-review/.nvmrc).

### Web app gets `401 Unauthorized`

Log in first at `/login`. The API is auth-protected by design.

## More Detail

For deeper operational notes, see [docs/runbook.md](/c:/Users/dipes/Documents/change-review/docs/runbook.md).
