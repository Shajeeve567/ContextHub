from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.models.memories import Memory
from api.app.schemas.memory import MemoryCreate


async def create_memory(db: AsyncSession, payload: MemoryCreate, embedding: Optional[List[float]] = None) -> Memory:
    memory = Memory(
        user_id=payload.user_id,
        project_id=payload.project_id,
        session_id=payload.session_id,
        memory_type=payload.memory_type,
        content=payload.content,
        embedding=embedding,
        importance=payload.importance,
        source=payload.source,
        meta_json=payload.meta_json,
    )
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    return memory


async def search_memories(
    db: AsyncSession,
    user_id: str,
    query_embedding: List[float],
    top_k: int = 10,
    project_id: Optional[str] = None,
) -> List[Tuple[Memory, float]]:
    filters = [Memory.user_id == user_id, Memory.embedding.isnot(None)]
    if project_id:
        filters.append(or_(Memory.project_id == project_id, Memory.project_id.is_(None)))

    stmt = select(
        Memory,
        (1 - Memory.embedding.cosine_distance(query_embedding)).label("score"),
    ).where(
        *filters,
    ).order_by(
        text("score DESC"),
    ).limit(top_k)

    result = await db.execute(stmt)
    return [(row[0], row[1]) for row in result.all()]


async def get_top_memories(db: AsyncSession, user_id: str, top_k: int = 10, project_id: Optional[str] = None) -> List[Memory]:
    filters = [Memory.user_id == user_id]
    if project_id:
        filters.append(or_(Memory.project_id == project_id, Memory.project_id.is_(None)))

    stmt = select(Memory).where(*filters).order_by(Memory.importance.desc()).limit(top_k)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_memories_by_type(db: AsyncSession, user_id: str, memory_type: str, project_id: Optional[str] = None) -> List[Memory]:
    filters = [Memory.user_id == user_id, Memory.memory_type == memory_type]
    if project_id:
        filters.append(or_(Memory.project_id == project_id, Memory.project_id.is_(None)))

    stmt = select(Memory).where(*filters).order_by(Memory.importance.desc(), Memory.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_memory_by_id(db: AsyncSession, memory_id: str) -> Optional[Memory]:
    result = await db.execute(select(Memory).where(Memory.id == memory_id))
    return result.scalar_one_or_none()


async def list_memories(db: AsyncSession, user_id: str, project_id: Optional[str] = None) -> List[Memory]:
    filters = [Memory.user_id == user_id]
    if project_id:
        filters.append(or_(Memory.project_id == project_id, Memory.project_id.is_(None)))

    stmt = select(Memory).where(*filters).order_by(Memory.importance.desc(), Memory.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_memory(db: AsyncSession, memory: Memory) -> None:
    await db.delete(memory)
    await db.commit()


async def increment_access_count(db: AsyncSession, memory_id: str) -> None:
    memory = await db.get(Memory, memory_id)
    if memory:
        memory.access_count = Memory.access_count + 1
        memory.last_accessed_at = datetime.now(timezone.utc)
        await db.commit()
