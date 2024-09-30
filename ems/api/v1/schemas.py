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
class Ven(BaseModel):
    name: str

class Venu(Ven):
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True

class Venue(Venu):
    capacity: Optional[int] = None

    class Config:
        from_attributes = True

class GetVenu(RootModel[List[Venu]]):
    pass

class GetVenue(RootModel[List[Venue]]):
    pass

# Ticket management schemas
class Tickt(BaseModel):
    type: TicketType
    price: Optional[float] = 0

class Ticket(Tickt):
    quantity: int
    booked: Optional[int] = 0

    class Config:
        from_attributes = True

class Tickts(RootModel[List[Tickt]]):
    pass

class Tickets(RootModel[List[Ticket]]):
    pass

# Event management schemas
class Evnt(BaseModel):
    id: int
    name: str
    starts: datetime
    
class Event(BaseModel):
    name: str
    description: Optional[str] = None
    starts: datetime
    event_ends: Optional[datetime] = None

class Events(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    starts: datetime
    event_ends: Optional[datetime] = None

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

class SearchEvents(BaseModel):
    Event: Evnt
    # Category: Category
    # Venue: Venue

    class Config:
        from_attributes = True

class SearchedEvent(Events):
    organizer: User
    category: Category
    venue: GetVenu
    tickets: Tickts

    class Config:
        from_attributes = True

# Booking management schemas
class Book(BaseModel):
    type: TicketType
    quantity: int

class Booked(BaseModel):
    event_date: datetime
    event_name: str
    event_venue: str
    event_description: str
    event_category: str
    event_organizer: str
    ticket_type: TicketType
    ticket_quantity: int
