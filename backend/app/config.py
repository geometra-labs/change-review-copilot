import os

# SQLite only; no auth, no migrations
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
