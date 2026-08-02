from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import get_settings

settings = get_settings()


def normalize_database_url(url: str) -> str:
    """Ensure SSL for Supabase/Neon and keep query params intact."""
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    host = (parsed.hostname or "").lower()

    if "supabase" in host or "neon.tech" in host:
        query.setdefault("sslmode", "require")

    return urlunparse(parsed._replace(query=urlencode(query)))


DATABASE_URL = normalize_database_url(settings.DATABASE_URL)
_is_transaction_pooler = ":6543" in DATABASE_URL or "pooler.supabase.com" in DATABASE_URL and "6543" in DATABASE_URL

engine_kwargs = {"pool_pre_ping": True}
if _is_transaction_pooler:
    # Supabase transaction pooler (PgBouncer) does not support server-side prepared statements well.
    engine_kwargs["poolclass"] = NullPool

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Enable pgvector and create tables."""
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    from app.models import attendance, embedding, search_log, user  # noqa: F401

    Base.metadata.create_all(bind=engine)
