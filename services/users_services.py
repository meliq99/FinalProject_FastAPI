from fastapi import HTTPException, status, Depends, Response, Request, Header
from fastapi.security import OAuth2PasswordBearer
from database import users_crud
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Optional
from jose import JWTError, jwt
from decouple import config
from utils import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

jwt_secret_key = config('SECRET_KEY')
jwt_algorithm = config('ALGORITHM')
jwt_access_token_expires = config('ACCESS_TOKEN_EXPIRE_MINUTES')
jwt_refresh_token_expires = config('REFRESH_TOKEN_EXPIRE_MINUTES')
api_key = config('API_KEY')


def get_user(db: Session, username: str):
    return users_crud.get_user(db, username)


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_secret_key,
                             algorithm=jwt_algorithm)
    return encoded_jwt


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(db, username)

    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")

    return user


async def login(username: str, password: str, db: Session, response: Response = None):
    user = authenticate_user(username, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(jwt_access_token_expires))
    access_token = create_jwt_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=int(jwt_refresh_token_expires))
    refresh_token = create_jwt_token(
        data={"sub": user.username, "role": user.role}, expires_delta=refresh_token_expires
    )

    new_refresh_token = users_crud.add_refresh_token(
        db, user.username, refresh_token)

    if not new_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Maximum number of sessions reached",
            headers={"WWW-Authenticate": "Bearer"},
        )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 15,  # 7 days
        expires=60 * 60 * 24 * 15,  # 7 days
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 5,  # 15 minutes
        expires=60 * 5,  # 15 minutes
    )

    response_user = {
        "username": user.username,
        "role": user.role,
        "refresh_token": refresh_token,
        "access_token": access_token,
    }

    return response_user


async def get_current_user(request: Request, response: Response = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        access_token = request.cookies.get('access_token')
        if not access_token:
            raise JWTError("Missing access token")

        payload = jwt.decode(access_token, jwt_secret_key,
                             algorithms=[jwt_algorithm])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None:
            raise credentials_exception
    except JWTError as e:
        print("JWT Error:", str(e))
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            raise credentials_exception

        new_access_token = await generate_access_token_from_refresh_token(refresh_token, response)
        try:
            payload = jwt.decode(
                new_access_token, jwt_secret_key, algorithms=[jwt_algorithm])
        except JWTError:
            raise credentials_exception

        username: str = payload.get("sub")
        role: str = payload.get("role")

    return {"username": username, "role": role}


async def create_user(user: dict, db: Session, response: Response = None):
    role = user.get('role') or 'user'

    refresh_token_expires = timedelta(minutes=int(jwt_refresh_token_expires))
    refresh_token = create_jwt_token(
        data={"sub": user['username'], "role": role}, expires_delta=refresh_token_expires
    )

    access_token_expires = timedelta(minutes=int(jwt_access_token_expires))
    access_token = create_jwt_token(
        data={"sub": user['username'], "role": role}, expires_delta=access_token_expires
    )

    user['tokens'] = [refresh_token]
    user['role'] = role

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 15,
        expires=60 * 60 * 24 * 15,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 5,
        expires=60 * 5,
    )

    user_in_db = users_crud.create_user(db, user)

    response_user = {
        "username": user_in_db.username,
        "role": user_in_db.role,
        "refresh_token": refresh_token,
        "access_token": access_token,
    }

    return response_user


async def generate_access_token_from_refresh_token(refresh_token: str, response: Response = None):
    print("test")
    db_session = next(db.get_db())
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token, jwt_secret_key,
                             algorithms=[jwt_algorithm])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception

        existent_refresh_token = users_crud.get_refresh_token(
            db_session, username, refresh_token)
        if not existent_refresh_token:
            raise credentials_exception

        access_token_expires = timedelta(minutes=int(jwt_access_token_expires))
        access_token = create_jwt_token(
            data={"sub": username, "role": role}, expires_delta=access_token_expires
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=60 * 5,  # 15 minutes
            expires=60 * 5,  # 15 minutes
        )

    except JWTError:
        raise credentials_exception

    return access_token


async def logout(db: Session, request: Request = None, response: Response = None):
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = jwt.decode(refresh_token, jwt_secret_key,
                         algorithms=[jwt_algorithm])

    username: str = payload.get("sub")
    users_crud.remove_refresh_token(db, username, refresh_token)

    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="access_token")

    return True


async def check_admin_role(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not admin",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


async def master_logout(db: Session, request: Request = None, response: Response = None):
    refresh_token = request.cookies.get('refresh_token')\

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = jwt.decode(refresh_token, jwt_secret_key,
                         algorithms=[jwt_algorithm])

    username: str = payload.get("sub")

    users_crud.remove_all_refresh_tokens(db, username)

    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="access_token")

    return True


async def create_admin_user(user: dict, db: Session, response: Response = None):
    role = "admin"

    refresh_toke_expires = timedelta(minutes=int(jwt_refresh_token_expires))
    refresh_token = create_jwt_token(
        data={"sub": user['username'], "role": role}, expires_delta=refresh_toke_expires
    )

    access_token_expires = timedelta(minutes=int(jwt_access_token_expires))
    access_token = create_jwt_token(
        data={"sub": user['username'], "role": role}, expires_delta=access_token_expires
    )

    user['tokens'] = [refresh_token]
    user['role'] = role

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 15,
        expires=60 * 60 * 24 * 15,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 5,
        expires=60 * 5,
    )

    user_in_db = users_crud.create_user(db, user)

    response_user = {
        "username": user_in_db.username,
        "role": user_in_db.role,
        "refresh_token": refresh_token,
        "access_token": access_token,
    }
    return response_user


def valid_api_key(x_api_key: str = Header(...)):
    if x_api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
