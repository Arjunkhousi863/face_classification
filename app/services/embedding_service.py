from __future__ import annotations

from typing import Optional

import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.embedding import FaceEmbedding
from app.models.user import User

settings = get_settings()


def save_embedding(db: Session, user: User, embedding: np.ndarray) -> FaceEmbedding:
    existing = db.query(FaceEmbedding).filter(FaceEmbedding.user_id == user.id).first()
    vector = embedding.astype(float).tolist()
    if existing:
        existing.embedding = vector
        db.add(existing)
        db.flush()
        return existing

    row = FaceEmbedding(user_id=user.id, embedding=vector)
    db.add(row)
    db.flush()
    return row


def delete_embedding(db: Session, user: User) -> None:
    db.query(FaceEmbedding).filter(FaceEmbedding.user_id == user.id).delete()
    db.flush()


def search_similar(
    db: Session,
    query_embedding: np.ndarray,
    threshold: Optional[float] = None,
) -> tuple[Optional[User], Optional[float]]:
    """
    Cosine distance via pgvector <=> operator.
    similarity = 1 - distance
    Match if similarity >= (1 - threshold) where threshold is max allowed distance.
    """
    max_distance = threshold if threshold is not None else settings.FACE_MATCH_THRESHOLD
    vector = query_embedding.astype(float).tolist()
    emb_literal = "[" + ",".join(f"{float(x):.8f}" for x in vector) + "]"

    sql = text(
        """
        SELECT fe.user_id AS uid, (fe.embedding <=> CAST(:emb AS vector)) AS distance
        FROM face_embeddings fe
        ORDER BY fe.embedding <=> CAST(:emb AS vector)
        LIMIT 1
        """
    )
    row = db.execute(sql, {"emb": emb_literal}).first()
    if not row:
        return None, None

    distance = float(row.distance)
    similarity = max(0.0, min(1.0, 1.0 - distance))
    if distance > max_distance:
        return None, similarity

    user = db.query(User).filter(User.id == row.uid).first()
    return user, similarity
