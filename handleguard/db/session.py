from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from handleguard.db.models import Base

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "handleguard.db"
_ENGINE: Engine | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None


def get_engine(url: str | None = None) -> Engine:
    global _ENGINE, _SESSION_FACTORY
    if url is None and _ENGINE is not None:
        return _ENGINE
    if url is None:
        DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{DEFAULT_DB}"
    engine = create_engine(url, future=True)
    if url is None or _ENGINE is None:
        _ENGINE = engine
        _SESSION_FACTORY = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return engine


def get_session() -> Session:
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        get_engine()
    assert _SESSION_FACTORY is not None
    return _SESSION_FACTORY()


def init_db(url: str | None = None) -> Engine:
    engine = get_engine(url)
    Base.metadata.create_all(engine)
    return engine


def reset_engine() -> None:
    global _ENGINE, _SESSION_FACTORY
    _ENGINE = None
    _SESSION_FACTORY = None
