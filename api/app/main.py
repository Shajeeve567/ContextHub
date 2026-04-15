from fastapi import FastAPI
from api.app.api.routes.documents import router as documents_router
from api.app.models import chunk
from api.app.api.routes.health import router as health_router
from api.app.api.routes.context_retrieval import router as context_router 
from api.app.api.routes.document_retrieval import router as retrieval_router
from api.app.core.config import settings
from api.app.core.database import Base, engine

from api.app.models import document 

from api.app.api.routes.projects import router as projects_router
from api.app.api.routes.sessions import router as sessions_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Personal Knowledge Memory API",
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(context_router)
    app.include_router(health_router)
    app.include_router(documents_router)
    app.include_router(retrieval_router)
    app.include_router(projects_router)
    app.include_router(sessions_router)

    return app


app = create_app()