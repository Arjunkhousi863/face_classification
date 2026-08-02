from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

_app = None
_model_error: Optional[str] = None


def get_face_app():
    """Lazy-load InsightFace FaceAnalysis (buffalo_l / ArcFace embeddings)."""
    global _app, _model_error
    if _app is not None:
        return _app
    if _model_error:
        raise RuntimeError(_model_error)

    try:
        from insightface.app import FaceAnalysis

        app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        _app = app
        logger.info("InsightFace model loaded")
        return _app
    except Exception as exc:  # noqa: BLE001
        _model_error = str(exc)
        logger.exception("Failed to load InsightFace")
        raise RuntimeError(f"Face model unavailable: {exc}") from exc


def is_model_ready() -> bool:
    try:
        get_face_app()
        return True
    except Exception:  # noqa: BLE001
        return False


def decode_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Invalid image file")
    return image


def get_face_embedding(file_bytes: bytes) -> np.ndarray:
    """Detect face and return L2-normalized 512-d embedding."""
    image = decode_image(file_bytes)
    app = get_face_app()
    faces = app.get(image)
    if not faces:
        raise ValueError("No face detected in image")
    # Largest face by bbox area
    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    embedding = np.asarray(face.normed_embedding, dtype=np.float32)
    if embedding.shape[0] != 512:
        raise ValueError(f"Unexpected embedding size: {embedding.shape[0]}")
    return embedding
