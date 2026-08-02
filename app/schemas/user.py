from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    role: str
    photo_url: Optional[str] = None
    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None
    role: Optional[str] = None


class UserCreateResponse(BaseModel):
    status: str = "success"
    user_id: str
    user: UserOut


class SearchResponse(BaseModel):
    found: bool
    similarity: Optional[float] = None
    user: Optional[UserOut] = None
    attendance_marked: bool = False
    attendance_message: Optional[str] = None
    message: Optional[str] = None


class PaginatedUsers(BaseModel):
    items: list[UserOut]
    page: int
    limit: int
    total: int
    pages: int


class HealthResponse(BaseModel):
    status: str
    app: str
    face_model_ready: bool
    details: dict[str, Any] = Field(default_factory=dict)
