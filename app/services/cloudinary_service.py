from typing import Optional

import cloudinary
import cloudinary.uploader

from app.config import get_settings

settings = get_settings()


def configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def upload_image(file_bytes: bytes, folder: str = "face_classification") -> dict:
    configure_cloudinary()
    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        resource_type="image",
    )
    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id"),
    }


def delete_image(public_id: Optional[str]) -> bool:
    if not public_id:
        return False
    configure_cloudinary()
    result = cloudinary.uploader.destroy(public_id)
    return result.get("result") == "ok"
