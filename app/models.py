from sqlalchemy import LargeBinary, String, Integer, Column
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase

load_dotenv()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    uuid_token = Column(String(40))


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    uuid_token = Column(String())
    user_id = Column(Integer)
    file = Column(LargeBinary, nullable=False)
    filename = Column(String(100), nullable=False)
