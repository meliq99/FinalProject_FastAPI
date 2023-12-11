from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from utils import db

Base = db.Base


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, index=True)
    password_hash = Column(String)
    role = Column(Enum('admin', 'user', 'guest'), default='user')
    tokens = Column(MutableList.as_mutable(JSONB), default=[])

