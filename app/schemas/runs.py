from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None