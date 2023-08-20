from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ..settings import settings

url = URL.create(**settings.postgres_connection.model_dump())
engine = create_engine(url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def session() -> SessionLocal:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()