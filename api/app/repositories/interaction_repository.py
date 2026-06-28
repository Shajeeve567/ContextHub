from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.models.interaction import Interaction


async def get_interactions_by_session(db: AsyncSession, session_id: str) -> List[Interaction]:
    result = await db.execute(
        select(Interaction)
        .where(Interaction.session_id == session_id)
        .order_by(Interaction.created_at.asc())
    )
    return list(result.scalars().all())
