from pydantic import BaseModel
from typing import List


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class Product(BaseModel):
    name: str
    description: str

class UserCreate(User):
    password: str

class UserUpdate(User):
    password: str

class UserDB(UserInDB):
    products: List[Product] = []
