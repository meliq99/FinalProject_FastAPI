from fastapi import APIRouter, HTTPException, status, Depends
from schemes import items_schemes
from database import items_crud
from sqlalchemy.orm import Session
from utils import db
from services.users_services import get_current_user
from typing import List

router = APIRouter(
    prefix='/items',
    tags=['Items']
)


@router.get('/', response_model=List[items_schemes.Item], status_code=status.HTTP_200_OK)
async def get_all_items(database: Session = Depends(db.get_db), current_user: dict = Depends(get_current_user)):
    username = current_user.get("username")
    # Assuming you have a function to get user by username

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    items = items_crud.get_all_items(database)
    return items
