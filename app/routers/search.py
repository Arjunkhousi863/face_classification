from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.search_log import SearchLog
from app.models.user import User
from app.schemas.user import SearchResponse, UserOut
from app.services import attendance_service, embedding_service, face_service
from app.utils.security import require_roles

router = APIRouter(prefix="/users", tags=["Search"])


@router.post("/search", response_model=SearchResponse)
async def search_face(
    request: Request,
    image: UploadFile = File(...),
    mark_attendance: str = Form("true"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "officer", "viewer")),
):
    """
    Search face in DB. If found and mark_attendance=true, mark Present for today.
    """
    should_mark = str(mark_attendance).strip().lower() in {"1", "true", "yes", "on"}
    file_bytes = await image.read()
    client_ip = request.client.host if request.client else None

    try:
        embedding = face_service.get_face_embedding(file_bytes)
    except ValueError as exc:
        log = SearchLog(
            searched_by=current_user.username,
            ip_address=client_ip,
            found=False,
            notes=str(exc),
        )
        db.add(log)
        db.commit()
        return SearchResponse(found=False, message=str(exc))
    except RuntimeError as exc:
        return SearchResponse(found=False, message=str(exc))

    user, similarity = embedding_service.search_similar(db, embedding)
    if not user:
        log = SearchLog(
            searched_by=current_user.username,
            ip_address=client_ip,
            found=False,
            similarity=similarity,
        )
        db.add(log)
        db.commit()
        return SearchResponse(found=False, similarity=similarity, message="No matching face found")

    attendance_marked = False
    attendance_message = None
    if should_mark:
        _, _created, msg = attendance_service.mark_present(
            db,
            user,
            similarity=similarity,
            marked_via="face_search",
        )
        attendance_marked = True
        attendance_message = msg

    log = SearchLog(
        searched_by=current_user.username,
        ip_address=client_ip,
        found=True,
        matched_user_id=user.user_id,
        similarity=similarity,
        attendance_marked=attendance_marked,
    )
    db.add(log)
    db.commit()

    return SearchResponse(
        found=True,
        similarity=round(similarity or 0.0, 4),
        user=UserOut.model_validate(user),
        attendance_marked=attendance_marked,
        attendance_message=attendance_message,
    )
