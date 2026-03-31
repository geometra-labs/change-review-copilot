from __future__ import annotations

from app.config import settings


def main() -> None:
    from redis import Redis
    from rq import Worker
    from rq.connections import Connection

    redis = Redis.from_url(settings.redis_url)
    with Connection(redis):
        worker = Worker(["crc"])
        worker.work()


if __name__ == "__main__":
    main()
