from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, Base, get_db
from app.api import projects, assemblies, change_events, impact


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="CAD Change-Impact API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(assemblies.router, prefix="/projects", tags=["assemblies"])
app.include_router(change_events.router, prefix="/projects", tags=["change-events"])
app.include_router(impact.router, prefix="/projects", tags=["impact"])
