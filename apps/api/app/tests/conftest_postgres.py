from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture()
def postgres_db_session() -> Generator[Session, None, None]:
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL not set")

    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def postgres_client(postgres_db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db():
        try:
            yield postgres_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
