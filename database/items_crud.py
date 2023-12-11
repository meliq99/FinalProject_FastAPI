from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import items_models
from schemes import items_schemes

def get_all_items(db: Session):
    items = db.query(items_models.Item).all()
    return items