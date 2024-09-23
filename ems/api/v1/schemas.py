###
from pydantic import BaseModel, RootModel, EmailStr
from typing import Optional, List
from datetime import datetime

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

# Venue management schemas
class Venue(BaseModel):
    name: str
    address: str
    city: str
    country: str
    capacity: int

class GetVenue(RootModel[List[Venue]]):
    pass

# Ticket management schemas
class Ticket(BaseModel):
    type: TicketType
    price: float
    quantity: int
    booked: Optional[int] = 0

class Tickets(RootModel[List[Ticket]]):
    pass

# Event management schemas
class Event(BaseModel):
    name: str
    description: str
    starts: datetime
    event_ends: datetime

class Events(BaseModel):
    id: int
    name: str
    description: str
    starts: datetime
    event_ends: datetime

class CreateEvent(Event):
    venue: Venue
    tickets: Tickets
    category: Category

    class Config:
        from_attributes = True

class CreatedEvent(Events):
    category: Category
    organizer: User
    venue: Venue
    tickets: Tickets

    class Config:
        from_attributes = True

class EventDetails(Event):
    category: Category
    organizer: User
    venue: GetVenue
    tickets: Tickets

    class Config:
        from_attributes = True

class Search(BaseModel):
    skip: int = 0
    limit: int = 10
    search: Optional[str] = ""
