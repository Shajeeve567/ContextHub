from api.app.core.database import Base 
from api.app.models.chunk import Chunk
from api.app.models.document import Document
from api.app.models.interaction import Interaction
from api.app.models.memories import Memory
from api.app.models.project_decisions import ProjectDecision
from api.app.models.project import Project
from api.app.models.session import Session
from api.app.models.user_preference import UserPreference


target_metadata = Base.metadata

__all__ = [
    "Base",
    "Chunk",
    "Document",
    "Interaction",
    "Memory",
    "Project",
    "ProjectDecision",
    "Session",
    "UserPreference",
]