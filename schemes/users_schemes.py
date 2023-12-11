# Models
from pydantic import BaseModel


class User(BaseModel):
    username: str


class UserInput(User):
    password: str


class UserInDB(User):
    password_hash: str


class UserCreated(User):
    role: str
    refresh_token: str
    access_token: str


class UserAuthenticated(User):
    role: str
    refresh_token: str
    access_token: str

class FullUser(User):
    id: int
    password_hash: str
    role: str
    tokens: list