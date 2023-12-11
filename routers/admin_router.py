from fastapi import APIRouter, HTTPException, status, Depends
from schemes import users_schemes
from database import users_crud
from sqlalchemy.orm import Session
from utils import db
from services.users_services import check_admin_role
from typing import List

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


@router.get('/{username}', response_model=users_schemes.FullUser, status_code=status.HTTP_200_OK)
async def get_full_user(username: str, database: Session = Depends(db.get_db), current_user: dict = Depends(check_admin_role)):

    user = users_crud.get_user(database, username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
