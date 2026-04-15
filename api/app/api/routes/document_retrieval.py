from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.core.database import get_db
from api.app.schemas.query import MemoryQueryRequest, MemoryQueryResponse, RetrievedChunk
from api.app.services.llm_service import generate_grounded_answer
from api.app.services.retrieval_service import search_relevant_chunks

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/ask", response_model=MemoryQueryResponse)
async def ask_memory_endpoint(payload: MemoryQueryRequest, db: AsyncSession = Depends(get_db)):
    results = await search_relevant_chunks(
        db=db,
        user_id=payload.user_id,
        question=payload.question,
        top_k=payload.top_k,
    )

    answer = await generate_grounded_answer(payload.question, results)

    sources = [
        RetrievedChunk(
            chunk_id=result["chunk"].id,
            document_id=result["chunk"].document_id,
            document_title=result["document_title"],
            chunk_index=result["chunk"].chunk_index,
            chunk_text=result["chunk"].chunk_text,
            score=result["score"],
        )
        for result in results
    ]

    return MemoryQueryResponse(
        question=payload.question,
        answer=answer,
        sources=sources,
    )

