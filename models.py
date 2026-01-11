from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from datetime import datetime

class ScrapeResult(BaseModel):
    url: str
    topic: str
    summary: str
    data: List[Any]
    timestamp: datetime = Field(default_factory=datetime.now)

class ScheduleConfig(BaseModel):
    url: str
    topic: str
    email: EmailStr
    frequency_days: int
    is_active: bool = True
