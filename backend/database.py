from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings


class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    return f"sqlite:///{settings.db_path}"


engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create the database file and all registered tables."""
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    import models  # noqa: F401 - register all models with Base.metadata

    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
