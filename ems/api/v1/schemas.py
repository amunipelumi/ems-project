###
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

###
from ...db.models import TicketType



# User management schemas
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

# Authentication schemas
class LoginUser(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    is_admin: Optional[bool]

# Event management schemas
class CreateEvent(BaseModel):
    name: str
    description: str
    starts: datetime
    event_ends: datetime
    venue_id: int
    category_id: int
    organizer_id: Optional[int] = 0
### *******
class CreateEventResp(BaseModel):
    id: int
    updated_at: datetime

class GetEvent(BaseModel):
    organizer_id: int
    event_id: int
    event_name: str
    event_type: str
    event_address: str
    event_description: str
    event_starts: datetime
    event_ends: datetime

class GetEvents(GetEvent):
    class Config:
        from_attributes = True

# Ticket management schemas
class CreateTicket(BaseModel):
    event: int
    type: TicketType
    price: float
    quantity: int
    owner: Optional[int]

class GetTickets(BaseModel):
    id: int
    event: int
    type: TicketType
    price: float
    quantity: int
    owner: Optional[int]
    updated_at: datetime
