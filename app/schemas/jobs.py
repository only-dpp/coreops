from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


JobType = Literal["http_check", "page_snapshot", "keyword_watch"]


class JobCreate(BaseModel):
    name: str
    type: JobType
    payload: dict = Field(default_factory=dict)


class JobUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[JobType] = None
    payload: Optional[dict] = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    type: str
    payload: dict
    created_at: datetime