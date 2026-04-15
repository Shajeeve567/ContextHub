from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.app.core.database import get_db
from api.app.services.context_service import get_project_context
from api.app.services.llm_service import generate_context_handoff
from api.app.schemas.context import LLMContext


router = APIRouter(prefix="/context", tags=["context"])

@router.get("")
def get_relevant_context(payload: LLMContext, db: Session = Depends(get_db)):
    context = get_project_context(db, payload.project_id, payload.user_id) # Project + Session logs
    if context is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    response = generate_context_handoff(context)
    return response



