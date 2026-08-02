from sqlalchemy.orm import Session

from app.models.user import User


def generate_user_id(db: Session) -> str:
    last = db.query(User).order_by(User.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"USR{next_num:04d}"
