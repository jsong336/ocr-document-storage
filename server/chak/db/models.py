from .connection import Base, engine
from sqlalchemy import Column, Integer, String, DateTime


class UserAccount(Base):
    id = Column(
        Integer,
        primary_key=True, 
        autoincrement=True
    )
    email = Column(
        String, 
        unique=True
    )


Base.metadata.create_all(engine)