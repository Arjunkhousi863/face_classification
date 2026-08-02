from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.user import User


def mark_present(
    db: Session,
    user: User,
    similarity: Optional[float] = None,
    marked_via: str = "face_search",
    attendance_date: Optional[date] = None,
) -> tuple[Attendance, bool, str]:
    """
    Mark user present for the day.
    Returns (attendance, created_new, message).
    """
    day = attendance_date or datetime.now(timezone.utc).date()
    existing = (
        db.query(Attendance)
        .filter(Attendance.user_id == user.id, Attendance.attendance_date == day)
        .first()
    )
    if existing:
        existing.status = "present"
        if similarity is not None:
            existing.similarity = similarity
        existing.marked_via = marked_via
        existing.marked_at = datetime.now(timezone.utc)
        db.add(existing)
        db.flush()
        return existing, False, f"Attendance already marked present for {user.name} on {day}"

    row = Attendance(
        user_id=user.id,
        attendance_date=day,
        status="present",
        similarity=similarity,
        marked_via=marked_via,
    )
    db.add(row)
    db.flush()
    return row, True, f"Attendance marked present for {user.name} on {day}"


def list_attendance(
    db: Session,
    attendance_date: Optional[date] = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[dict], int]:
    day = attendance_date or datetime.now(timezone.utc).date()
    q = (
        db.query(Attendance, User)
        .join(User, User.id == Attendance.user_id)
        .filter(Attendance.attendance_date == day)
        .order_by(Attendance.marked_at.desc())
    )
    total = q.count()
    rows = q.offset((page - 1) * limit).limit(limit).all()
    items = [
        {
            "id": att.id,
            "user_id": user.user_id,
            "name": user.name,
            "photo_url": user.photo_url,
            "attendance_date": att.attendance_date,
            "status": att.status,
            "similarity": att.similarity,
            "marked_via": att.marked_via,
            "marked_at": att.marked_at,
        }
        for att, user in rows
    ]
    return items, total


def attendance_stats(db: Session, attendance_date: Optional[date] = None) -> dict:
    day = attendance_date or datetime.now(timezone.utc).date()
    present = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.attendance_date == day, Attendance.status == "present")
        .scalar()
        or 0
    )
    # Face-registered people (exclude login-only admin seed without photo)
    total_users = (
        db.query(func.count(User.id)).filter(User.photo_url.isnot(None)).scalar() or 0
    )
    return {"date": day, "present": present, "total_users": total_users}
