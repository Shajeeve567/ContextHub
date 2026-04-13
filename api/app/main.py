from fastapi import FastAPI

from api.app.api.routes.documents import router as documents_router
from api.app.models import chunk
from api.app.api.routes.health import router as health_router
from api.app.api.routes.retrieval import router as retrieval_router
from api.app.core.config import settings
from api.app.core.database import Base, engine

# Import models so SQLAlchemy registers them before create_all()
from api.app.models import document  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Personal Knowledge Memory API",
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(health_router)
    app.include_router(documents_router)
    app.include_router(retrieval_router)

    return app


app = create_app()