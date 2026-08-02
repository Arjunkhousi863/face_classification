from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    name: str
    photo_url: Optional[str] = None
    attendance_date: date
    status: str
    similarity: Optional[float] = None
    marked_via: str
    marked_at: datetime


class AttendanceStats(BaseModel):
    date: date
    present: int
    total_users: int
