from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database.session import engine
from app.schemas.user import HealthResponse
from app.services.face_service import is_model_ready

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
def health():
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False

    face_ready = is_model_ready()
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        app=settings.APP_NAME,
        face_model_ready=face_ready,
        details={
            "database": "up" if db_ok else "down",
            "cloudinary_configured": bool(settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY),
        },
    )
