import asyncio
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession

from api.app.core.database import AsyncSessionLocal
from api.app.repositories import memory_repository
from api.app.repositories import session_repository as session_repo
from api.app.repositories import interaction_repository
from api.app.schemas.memory import MemoryCreate, MemorySearchResult
from api.app.schemas.memory import MemoryResponse
from api.app.services.infrastructure.embedding_service import STMEmbedding
from api.app.services.infrastructure.llm_service import call_llm
from api.app.services.infrastructure.prompt_service import MEMORY_EXTRACTION_SYSTEM_PROMPT


class MemoryService:
    def __init__(self):
        self.embedder = STMEmbedding()

    async def create_memory(
        self, db: AsyncSession, payload: MemoryCreate
    ) -> MemoryResponse:
        embedding = self.embedder.embed_query(payload.content)
        memory = await memory_repository.create_memory(db, payload, embedding)
        return MemoryResponse.model_validate(memory)

    async def extract_memories_from_session(self, session_id: str) -> None:
        try:
            async with AsyncSessionLocal() as db:
                session = await session_repo.get_session_by_id(db, session_id)
                if not session:
                    logger.warning("extract_memories: session %s not found", session_id)
                    return

                interactions = await interaction_repository.get_interactions_by_session(db, session_id)

                user_prompt = self._build_extraction_prompt(session, interactions)
                raw = await asyncio.to_thread(call_llm, MEMORY_EXTRACTION_SYSTEM_PROMPT, user_prompt)
                candidates = self._parse_extraction_result(raw)

                for c in candidates:
                    payload = MemoryCreate(
                        user_id=session.user_id,
                        project_id=session.project_id,
                        session_id=session.id,
                        memory_type=c["memory_type"],
                        content=c["content"],
                        importance=c["importance"],
                        source="extraction",
                    )
                    embedding = self.embedder.embed_query(c["content"])
                    await memory_repository.create_memory(db, payload, embedding)

                logger.info("extracted %d memories from session %s", len(candidates), session_id)
        except Exception:
            logger.exception("extract_memories failed for session %s", session_id)

    def _build_extraction_prompt(self, session, interactions) -> str:
        lines = [f"Session summary:"]
        if session.worked_on:
            lines.append(f"Worked on: {session.worked_on}")
        if session.progress:
            lines.append(f"Progress: {session.progress}")
        if session.pending:
            lines.append(f"Pending: {', '.join(session.pending)}")
        if session.blockers:
            lines.append(f"Blockers: {', '.join(session.blockers)}")

        if interactions:
            lines.append(f"\nConversation log:")
            for i in interactions[-20:]:
                lines.append(f"User: {i.user_message[:300]}")
                lines.append(f"AI: {i.ai_response[:300]}")

        return "\n".join(lines) if len(lines) > 1 else "No session data available."

    def _parse_extraction_result(self, raw: Optional[str]) -> List[dict]:
        if not raw:
            return []

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0]

        try:
            candidates = json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start != -1 and end != -1:
                try:
                    candidates = json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    return []
            else:
                return []

        if not isinstance(candidates, list):
            return []

        valid = []
        for c in candidates:
            if isinstance(c, dict) and c.get("content") and c.get("memory_type"):
                valid.append({
                    "memory_type": c["memory_type"],
                    "content": c["content"],
                    "importance": min(max(float(c.get("importance", 0.5)), 0.0), 1.0),
                })
        return valid

    async def search_memories(
        self, db: AsyncSession, user_id: str, query: str, top_k: int = 10, project_id: Optional[str] = None
    ) -> List[MemorySearchResult]:
        query_embedding = self.embedder.embed_query(query)
        results = await memory_repository.search_memories(db, user_id, query_embedding, top_k, project_id=project_id)

        out = []
        for memory, score in results:
            out.append(MemorySearchResult(
                id=memory.id,
                content=memory.content,
                memory_type=memory.memory_type,
                importance=memory.importance,
                score=round(float(score), 4),
                created_at=memory.created_at,
            ))
            await memory_repository.increment_access_count(db, memory.id)
        return out

    async def get_relevant_memories(
        self,
        db: AsyncSession,
        user_id: str,
        project_goal: Optional[str] = None,
        project_id: Optional[str] = None,
        top_k: int = 10,
    ) -> List[dict]:
        important = await memory_repository.get_top_memories(db, user_id, top_k=top_k, project_id=project_id)

        semantic: list = []
        if project_goal:
            goal_embedding = self.embedder.embed_query(project_goal)
            semantic = await memory_repository.search_memories(db, user_id, goal_embedding, top_k=top_k, project_id=project_id)
            semantic = [m for m, _ in semantic]

        seen = set()
        merged = []
        for m in important + semantic:
            if m.id not in seen:
                seen.add(m.id)
                merged.append({
                    "id": m.id,
                    "content": m.content,
                    "memory_type": m.memory_type,
                    "importance": m.importance,
                })

        return merged[:top_k]

    async def delete_memory(self, db: AsyncSession, memory_id: str) -> bool:
        memory = await memory_repository.get_memory_by_id(db, memory_id)
        if not memory:
            return False
        await memory_repository.delete_memory(db, memory)
        return True
