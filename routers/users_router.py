from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from schemes import users_schemes
from database import users_crud
from services import users_services
from sqlalchemy.orm import Session
from utils import db

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('/register', response_model=users_schemes.UserAuthenticated, status_code=status.HTTP_201_CREATED)
async def create_user(user: users_schemes.UserInput, database: Session = Depends(db.get_db), response: Response = None):
    user_dict = user.model_dump()
    user_created = await users_services.create_user(user_dict, database, response)
    return user_created


@router.post('/authenticate', response_model=users_schemes.UserAuthenticated, status_code=status.HTTP_200_OK)
async def authenticate_user(user: users_schemes.UserInput, database: Session = Depends(db.get_db), response: Response = None):
    user_dict = user.model_dump()
    authenticated_user = await users_services.login(
        user_dict['username'], user_dict['password'], database, response)

    return authenticated_user


@router.post('/logout', status_code=status.HTTP_200_OK)
async def logout_user(database: Session = Depends(db.get_db), request: Request = None, response: Response = None):
    await users_services.logout(database, request, response)

    return {"message": "User logged out successfully"}


@router.post('/master-logout', status_code=status.HTTP_200_OK)
async def master_logout_user(database: Session = Depends(db.get_db), request: Request = None, response: Response = None):
    await users_services.master_logout(database, request, response)

    return {"message": "Logged from all devices successfully"}


@router.post('/create-admin', response_model=users_schemes.UserAuthenticated, status_code=status.HTTP_201_CREATED)
async def create_admin_user(user: users_schemes.UserInput, database: Session = Depends(db.get_db), response: Response = None, api_key: str = Depends(users_services.valid_api_key)):
    user_dict = user.model_dump()
    user_created = await users_services.create_admin_user(user_dict, database, response)
    return user_created
