from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.app.core.database import get_db
from api.app.services.context_service import get_project_context
from api.app.services.llm_service import generate_context_handoff



router = APIRouter(prefix="/context", tags=["context"])

@router.get("")
def get_relevant_context(user_id: str, project_id: str, db: Session = Depends(get_db)):
    context = get_project_context(db, project_id, user_id) # Project + Session logs
    response = generate_context_handoff(context)
    return response



