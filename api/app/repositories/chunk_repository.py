from typing import List

from sqlalchemy.orm import Session, joinedload

from api.app.models.chunk import Chunk
from api.app.models.document import Document


def replace_chunks_for_document(db: Session, document_id: str, chunk_payloads: List[dict]) -> List[Chunk]:
    db.query(Chunk).filter(Chunk.document_id == document_id).delete(synchronize_session=False)

    chunks: List[Chunk] = []
    for payload in chunk_payloads:
        chunk = Chunk(
            document_id=document_id,
            chunk_index=payload["chunk_index"],
            chunk_text=payload["chunk_text"],
            token_count=payload["token_count"],
            embedding=payload["embedding"],
            meta_json=payload.get("meta_json", {}),
        )
        chunks.append(chunk)

    db.add_all(chunks)
    db.commit()

    for chunk in chunks:
        db.refresh(chunk)

    return chunks


def get_chunks_for_user(db: Session, user_id: str) -> List[Chunk]:
    return (
        db.query(Chunk)
        .join(Document, Chunk.document_id == Document.id)
        .options(joinedload(Chunk.document))
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc(), Chunk.chunk_index.asc())
        .all()
    )


def get_chunks_for_document(db: Session, document_id: str) -> List[Chunk]:
    return (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index.asc())
        .all()
    )