from __future__ import annotations

import json
import pathlib
import shutil
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

ROOT = pathlib.Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.models.core import ModelVersion, Project, User  # noqa: E402
from app.services.parse_service import ParseService  # noqa: E402
from app.services.persistence_service import PersistenceService  # noqa: E402

FIXTURES = ROOT / "data" / "fixtures"
LOCAL_STORAGE = ROOT / ".local_storage" / "seeded"


def ensure_fixture_files() -> tuple[pathlib.Path, pathlib.Path]:
    LOCAL_STORAGE.mkdir(parents=True, exist_ok=True)

    before_path = FIXTURES / "demo_before.json"
    after_path = FIXTURES / "demo_after.json"

    if not before_path.exists() or not after_path.exists():
        raise FileNotFoundError("Missing demo fixture files in data/fixtures")

    target_before = LOCAL_STORAGE / "demo_before.json"
    target_after = LOCAL_STORAGE / "demo_after.json"

    shutil.copyfile(before_path, target_before)
    shutil.copyfile(after_path, target_after)

    return target_before, target_after


def main() -> None:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    target_before, target_after = ensure_fixture_files()
    parser = ParseService()
    persistence = PersistenceService()

    with session_local() as db:
        user = db.scalar(select(User).where(User.email == "demo@example.com"))
        if not user:
            user = User(email="demo@example.com", password_hash=hash_password("password123"))
            db.add(user)
            db.commit()
            db.refresh(user)

        project = db.scalar(select(Project).where(Project.name == "Demo Project"))
        if not project:
            project = Project(owner_id=user.id, name="Demo Project", description="Seeded demo project")
            db.add(project)
            db.commit()
            db.refresh(project)

        before_mv = db.scalar(
            select(ModelVersion).where(
                ModelVersion.project_id == project.id,
                ModelVersion.label == "before",
            )
        )
        if not before_mv:
            before_mv = ModelVersion(
                project_id=project.id,
                label="before",
                source_type="normalized_json",
                file_uri=str(target_before),
                parse_status="uploaded",
            )
            db.add(before_mv)
            db.commit()
            db.refresh(before_mv)
        else:
            before_mv.file_uri = str(target_before)
            before_mv.source_type = "normalized_json"
            before_mv.parse_status = "uploaded"
            before_mv.parse_error = None
            db.commit()

        after_mv = db.scalar(
            select(ModelVersion).where(
                ModelVersion.project_id == project.id,
                ModelVersion.label == "after",
            )
        )
        if not after_mv:
            after_mv = ModelVersion(
                project_id=project.id,
                label="after",
                source_type="normalized_json",
                file_uri=str(target_after),
                parse_status="uploaded",
            )
            db.add(after_mv)
            db.commit()
            db.refresh(after_mv)
        else:
            after_mv.file_uri = str(target_after)
            after_mv.source_type = "normalized_json"
            after_mv.parse_status = "uploaded"
            after_mv.parse_error = None
            db.commit()

        normalized_before = parser.parse_model(before_mv.file_uri)
        persistence.replace_model_contents(db, before_mv, normalized_before)

        normalized_after = parser.parse_model(after_mv.file_uri)
        persistence.replace_model_contents(db, after_mv, normalized_after)

        db.commit()

        print(
            json.dumps(
                {
                    "user_email": user.email,
                    "user_password": "password123",
                    "project_id": str(project.id),
                    "before_model_version_id": str(before_mv.id),
                    "after_model_version_id": str(after_mv.id),
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
