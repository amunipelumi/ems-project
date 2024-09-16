###
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

###
from ...db.models import TicketType



# User management schemas
class User(BaseModel):
    name: str
    
class UserTable(User):
    username: str
    email: EmailStr
    phone_number: Optional[str] = "0"

    class Config:
        from_attributes = True

class CreateUser(UserTable):
    is_admin: Optional[bool] = False
    password: str

    class Config:
        from_attributes = True

class CreateAdmin(UserTable):
    is_admin: Optional[bool] = True
    password: str

    class Config:
        from_attributes = True

class GetUser(UserTable):
    id: int

    class Config:
        from_attributes = True

class GetAdmin(UserTable):
    id: int
    is_admin: bool

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

# Category management schema
class Category(BaseModel):
    name: str
    description: Optional[str] = 'Not yet'

# Venue management schemas
class Venue(BaseModel):
    name: str
    address: str
    city: str
    country: str
    capacity: int

class GetVenue(Venue):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Ticket management schemas
class Ticket(BaseModel):
    type: TicketType
    price: float
    quantity: int

class TicketTable(Ticket):
    event: int
    owner: Optional[int]

    class Config:
        from_attributes = True

class GetTicket(TicketTable):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Event management schemas
class Event(BaseModel):
    name: str
    description: str
    starts: datetime
    event_ends: datetime

class EventTable(Event):
    venue_id: int
    category_id: int

    class Config:
        from_attributes = True

class GetEvent(EventTable):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
### ********************* ###
# I have to make sure I do some database check for potential conflicts

class CreateEventMain(BaseModel):
    event: Event
    venue: Venue
    category: Category

    class Config:
        from_attributes = True

class CreateEventResp(BaseModel):
    event: Event
    venue: Venue
    organizer: User
    category: Category

    class Config:
        from_attributes = True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~