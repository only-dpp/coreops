from datetime import datetime
from typing import Literal, Optional, Any

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from typing import Optional

JobType = Literal["http_check", "page_snapshot", "keyword_watch"]


class MonitorSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    enabled: bool
    status: str
    interval_seconds: int
    last_checked_at: Optional[datetime] = None
    last_error: Optional[str] = None
    consecutive_failures: int
    next_run_at: Optional[datetime] = None

class JobCreate(BaseModel):
    name: str
    type: JobType
    payload: dict = Field(default_factory=dict)
    interval_seconds: int = 60
    enabled: bool = True
    alert_channel: str = "discord"
    alert_target: str | None = None


class JobUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[JobType] = None
    payload: Optional[dict] = None
    interval_seconds: Optional[int] = None
    enabled: Optional[bool] = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    type: str
    payload: dict
    created_at: datetime

    interval_seconds: int
    enabled: bool
    next_run_at: Optional[datetime] = None

    alert_channel: str
    alert_target: Optional[str] = None

    last_status: Optional[str] = None
    last_checked_at: Optional[datetime] = None
    last_error: Optional[str] = None
    last_output: Optional[dict[str, Any]] = None
    consecutive_failures: int