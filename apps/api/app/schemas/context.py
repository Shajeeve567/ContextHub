from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class LLMContext(BaseModel):
    session_id: str
    project_id: str
    