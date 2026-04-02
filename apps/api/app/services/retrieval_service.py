from typing import List

from sqlalchemy.orm import Session

from app.repositories.chunk_repository import get_chunks_for_user
# from app.services.embedding_service import embed_text
from app.services.embedding_service import STMEmbedding


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    return sum(a * b for a, b in zip(vec_a, vec_b))


def search_relevant_chunks(db: Session, user_id: str, question: str, top_k: int = 5) -> List[dict]:

    embedding = STMEmbedding()

    query_embedding = embedding.embed_query(question)
    chunks = get_chunks_for_user(db, user_id)

    scored_results: List[dict] = []

    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk.embedding or [])
        scored_results.append(
            {
                "chunk": chunk,
                "score": round(float(score), 6),
                "document_title": chunk.document.title if chunk.document else "Untitled Document",
            }
        )

    scored_results.sort(key=lambda item: item["score"], reverse=True)
    return scored_results[:top_k]