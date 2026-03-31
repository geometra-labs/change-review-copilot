from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.artifacts import router as artifacts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.comparisons import router as comparisons_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.model_versions import router as model_versions_router
from app.api.routes.parsers import router as parsers_router
from app.api.routes.parse import router as parse_router
from app.api.routes.projects import router as projects_router
from app.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(title="Change Review Copilot API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(model_versions_router)
    app.include_router(parse_router)
    app.include_router(parsers_router)
    app.include_router(comparisons_router)
    app.include_router(jobs_router)
    app.include_router(artifacts_router)

    return app


app = create_app()
