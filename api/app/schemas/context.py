from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class LLMContext(BaseModel):
    user_id: str
    project_id: str
    