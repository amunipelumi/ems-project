from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional



class User(BaseModel):
    name: str
    username: str
    email: EmailStr
    phone_number: Optional[str] = "0"
    

class GetUser(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    phone_number: Optional[str] = "0"
    created_at: datetime


class CreateUser(User):
    password: str
    pass


class GetUsers(GetUser):
    class Config:
        from_attributes = True


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None