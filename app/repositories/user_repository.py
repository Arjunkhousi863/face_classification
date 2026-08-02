from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.ids import generate_user_id


def create_user(
    db: Session,
    *,
    name: str,
    phone: Optional[str],
    address: Optional[str],
    occupation: Optional[str],
    role: str,
    photo_url: Optional[str],
    photo_public_id: Optional[str],
) -> User:
    user = User(
        user_id=generate_user_id(db),
        name=name,
        phone=phone,
        address=address,
        occupation=occupation,
        role=role or "viewer",
        photo_url=photo_url,
        photo_public_id=photo_public_id,
    )
    db.add(user)
    db.flush()
    return user


def get_by_public_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()


def get_by_pk(db: Session, pk: int) -> Optional[User]:
    return db.query(User).filter(User.id == pk).first()


def list_users(db: Session, page: int = 1, limit: int = 20) -> tuple[list[User], int]:
    q = db.query(User).order_by(User.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()
    return items, total


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.flush()
