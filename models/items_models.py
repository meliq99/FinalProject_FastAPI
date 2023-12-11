from sqlalchemy import Column, Integer, String
from utils import db

Base = db.Base

class Item(Base):
    __tablename__ = 'items'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)