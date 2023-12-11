from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import users_models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, username: str):
    User = users_models.User
    user = db.query(User).filter(User.username == username).first()
    return user


def create_user(db: Session, user: dict):
    User = users_models.User
    username = user.get('username')
    password = user.get('password')
    tokens = user.get('tokens')
    role = user.get('role') or None

    user_in_db = db.query(User).filter(User.username == username).first()

    if user_in_db:
        raise HTTPException(status_code=400, detail="Username already taken")

    password_hash = pwd_context.hash(password)

    db_user = User(username=username, password_hash=password_hash,
                   tokens=tokens, role=role)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_refresh_token(db: Session, username: str, refresh_token: str):
    User = users_models.User

    # Query to retrieve the user's tokens
    user_record = db.query(User).filter(User.username == username).first()

    # Check if the user exists and has the specified refresh token
    if user_record and refresh_token in user_record.tokens:
        return refresh_token


def add_refresh_token(db: Session, username: str, new_refresh_token: str):
    User = users_models.User

    # Retrieve the user record
    user_record = db.query(User).filter(User.username == username).first()

    if len(user_record.tokens) >= 5:
        # Block the user from logging in
        return None
    # Append the new token to the user's tokens list
    if user_record.tokens is None:
        user_record.tokens = [new_refresh_token]
    else:
        user_record.tokens.append(new_refresh_token)

    # Commit the changes to the database
    db.commit()
    db.refresh(user_record)

    return new_refresh_token


def remove_refresh_token(db: Session, username: str, refresh_token: str):
    User = users_models.User

    # Retrieve the user record
    user_record = db.query(User).filter(User.username == username).first()

    # Remove the token from the user's tokens list
    user_record.tokens.remove(refresh_token)

    # Commit the changes to the database
    db.commit()
    db.refresh(user_record)

    return refresh_token


def remove_all_refresh_tokens(db: Session, username: str):
    User = users_models.User

    # Retrieve the user record
    user_record = db.query(User).filter(User.username == username).first()

    # Remove all tokens from the user's tokens list
    user_record.tokens = []

    # Commit the changes to the database
    db.commit()
    db.refresh(user_record)

    return user_record.tokens