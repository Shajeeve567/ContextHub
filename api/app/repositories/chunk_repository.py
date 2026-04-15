from typing import List

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.app.models.chunk import Chunk
from api.app.models.document import Document


async def replace_chunks_for_document(db: AsyncSession, document_id: str, chunk_payloads: List[dict]) -> List[Chunk]:
    await db.execute(delete(Chunk).where(Chunk.document_id == document_id))

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
    await db.commit()

    for chunk in chunks:
        await db.refresh(chunk)

    return chunks


async def get_chunks_for_user(db: AsyncSession, user_id: str) -> List[Chunk]:
    result = await db.execute(
        select(Chunk)
        .join(Document, Chunk.document_id == Document.id)
        .options(selectinload(Chunk.document))
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc(), Chunk.chunk_index.asc())
    )
    return list(result.scalars().all())


async def get_chunks_for_document(db: AsyncSession, document_id: str) -> List[Chunk]:
    result = await db.execute(
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index.asc())
    )
    return list(result.scalars().all())