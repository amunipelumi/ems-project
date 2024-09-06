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
    phone_number: str
    created_at: datetime

class GetAdmin(GetUser):
    is_admin: bool

class CreateUser(User):
    is_admin: Optional[bool] = False
    password: str

class CreateAdmin(User):
    is_admin: Optional[bool] = True
    password: str

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
    is_admin: Optional[bool]