# Runbook

## Local startup

1. copy `.env.example` to `.env`
2. run `docker-compose up -d db`
3. run migrations
4. seed demo data
5. start api
6. start web

### Commands

Unix-like shells:

- `make migrate`
- `make api`
- `make web`

Windows:

- `.\dev.cmd migrate`
- `python scripts/seed_demo_data.py`
- `.\dev.cmd api`
- `.\dev.cmd web`

## Common failure modes

### parse stuck in queued

- check worker
- check db connection
- inspect job logs

### upload succeeds but parse fails

- inspect file type
- inspect `parse_error`
- retry with demo fixture

### report missing explanation

- check explanation provider availability
- structured report should still render

## Release checklist

- migrations applied
- smoke tests passing
- demo fixture run passing
- structured logs enabled
- error monitoring configured

## Queue-backed mode

Set:
- `TASK_BACKEND=rq`
- `REDIS_URL=redis://localhost:6379/0`

Then run:
1. `docker-compose up -d`
2. `make api`
3. `make worker`

In queue-backed mode:
- routes create `JobRun` rows
- tasks are enqueued to Redis/RQ
- worker process executes parse/comparison
- UI polls `/jobs/{id}`
