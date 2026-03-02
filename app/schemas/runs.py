<<<<<<< HEAD
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
=======
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
>>>>>>> 21599b0b39eba37876fc43d9838497fbe2974000
    error: Optional[str] = None