import math
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.attendance import AttendanceOut, AttendanceStats
from app.services import attendance_service
from app.utils.security import require_roles

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("", response_model=dict)
def list_today_attendance(
    attendance_date: Optional[date] = Query(None),
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "officer", "viewer")),
):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    items, total = attendance_service.list_attendance(
        db, attendance_date=attendance_date, page=page, limit=limit
    )
    return {
        "items": [AttendanceOut(**i) for i in items],
        "page": page,
        "limit": limit,
        "total": total,
        "pages": max(1, math.ceil(total / limit)) if total else 1,
    }


@router.get("/stats", response_model=AttendanceStats)
def stats(
    attendance_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "officer", "viewer")),
):
    return AttendanceStats(**attendance_service.attendance_stats(db, attendance_date))
