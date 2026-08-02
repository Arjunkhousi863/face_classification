from __future__ import annotations

import logging
import os
import threading
from typing import Optional

# Keep CPU math libraries from spawning many threads (saves RAM on Render free).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("ORT_NUM_THREADS", "1")

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# buffalo_sc is the smallest InsightFace pack; still may need >512MB on free Render.
FACE_MODEL_NAME = os.getenv("FACE_MODEL_NAME", "buffalo_sc")
DET_SIZE = int(os.getenv("FACE_DET_SIZE", "256"))

_app = None
_model_error: Optional[str] = None
_lock = threading.Lock()


def get_face_app():
    """Lazy-load InsightFace with only detection + recognition modules."""
    global _app, _model_error
    if _app is not None:
        return _app
    if _model_error:
        raise RuntimeError(_model_error)

    with _lock:
        if _app is not None:
            return _app
        if _model_error:
            raise RuntimeError(_model_error)
        try:
            from insightface.app import FaceAnalysis

            logger.info("Loading InsightFace model: %s (detection+recognition only)", FACE_MODEL_NAME)
            app = FaceAnalysis(
                name=FACE_MODEL_NAME,
                allowed_modules=["detection", "recognition"],
                providers=["CPUExecutionProvider"],
            )
            app.prepare(ctx_id=-1, det_size=(DET_SIZE, DET_SIZE))
            _app = app
            logger.info("InsightFace model loaded")
            return _app
        except Exception as exc:  # noqa: BLE001
            _model_error = str(exc)
            logger.exception("Failed to load InsightFace")
            raise RuntimeError(f"Face model unavailable: {exc}") from exc


def is_model_ready() -> bool:
    return _app is not None


def warmup_model() -> None:
    def _run():
        try:
            get_face_app()
        except Exception:  # noqa: BLE001
            logger.exception("Face model warmup failed")

    threading.Thread(target=_run, name="face-warmup", daemon=True).start()


def decode_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Invalid image file")
    # Downscale huge images to reduce RAM during inference
    h, w = image.shape[:2]
    max_side = int(os.getenv("FACE_MAX_IMAGE_SIDE", "640"))
    scale = min(1.0, max_side / max(h, w))
    if scale < 1.0:
        image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return image


def get_face_embedding(file_bytes: bytes) -> np.ndarray:
    """Detect face and return L2-normalized 512-d embedding."""
    image = decode_image(file_bytes)
    app = get_face_app()
    faces = app.get(image)
    if not faces:
        raise ValueError("No face detected in image")
    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    embedding = np.asarray(face.normed_embedding, dtype=np.float32)
    if embedding.shape[0] != 512:
        raise ValueError(f"Unexpected embedding size: {embedding.shape[0]}")
    return embedding
