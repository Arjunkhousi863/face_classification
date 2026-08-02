import math
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.repositories import user_repository as users_repo
from app.schemas.user import PaginatedUsers, UserCreateResponse, UserOut, UserUpdate
from app.services import cloudinary_service, embedding_service, face_service
from app.utils.security import require_roles

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    name: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    occupation: Optional[str] = Form(None),
    role: str = Form("viewer"),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "officer")),
):
    file_bytes = await image.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Image is required")

    try:
        embedding = face_service.get_face_embedding(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        uploaded = cloudinary_service.upload_image(file_bytes)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Image upload failed: {exc}") from exc

    user = users_repo.create_user(
        db,
        name=name,
        phone=phone,
        address=address,
        occupation=occupation,
        role=role,
        photo_url=uploaded["url"],
        photo_public_id=uploaded["public_id"],
    )
    embedding_service.save_embedding(db, user, embedding)
    db.commit()
    db.refresh(user)
    return UserCreateResponse(status="success", user_id=user.user_id, user=UserOut.model_validate(user))


@router.get("", response_model=PaginatedUsers)
def get_all_users(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "officer", "viewer")),
):
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    items, total = users_repo.list_users(db, page=page, limit=limit)
    return PaginatedUsers(
        items=[UserOut.model_validate(u) for u in items],
        page=page,
        limit=limit,
        total=total,
        pages=max(1, math.ceil(total / limit)) if total else 1,
    )


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "officer", "viewer")),
):
    user = users_repo.get_by_public_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    occupation: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "officer")),
):
    user = users_repo.get_by_public_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if name is not None:
        user.name = name
    if phone is not None:
        user.phone = phone
    if address is not None:
        user.address = address
    if occupation is not None:
        user.occupation = occupation
    if role is not None:
        user.role = role

    if image is not None:
        file_bytes = await image.read()
        if file_bytes:
            try:
                embedding = face_service.get_face_embedding(file_bytes)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            cloudinary_service.delete_image(user.photo_public_id)
            embedding_service.delete_embedding(db, user)

            uploaded = cloudinary_service.upload_image(file_bytes)
            user.photo_url = uploaded["url"]
            user.photo_public_id = uploaded["public_id"]
            embedding_service.save_embedding(db, user, embedding)

    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    user = users_repo.get_by_public_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cloudinary_service.delete_image(user.photo_public_id)
    users_repo.delete_user(db, user)
    db.commit()
    return {"status": "success", "message": f"Deleted {user_id}"}
