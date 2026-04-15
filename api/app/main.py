from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.app.api.routes.documents import router as documents_router
from api.app.api.routes.health import router as health_router
from api.app.api.routes.context_retrieval import router as context_router 
from api.app.api.routes.document_retrieval import router as retrieval_router
from api.app.core.config import settings
from api.app.core.database import init_db

from api.app.api.routes.projects import router as projects_router
from api.app.api.routes.sessions import router as sessions_router
from api.app import models as _models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Personal Knowledge Memory API",
        lifespan=lifespan,
    )

    app.include_router(context_router)
    app.include_router(health_router)
    app.include_router(documents_router)
    app.include_router(retrieval_router)
    app.include_router(projects_router)
    app.include_router(sessions_router)

    return app


app = create_app()