###
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text, Enum 
# from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

###
from .database import Base

###
import enum



# Ticket Type
class TicketType(enum.Enum):
    VIP = "VIP"
    REGULAR = "Regular"
    FREE = "Free"

# User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(100), nullable=False)
    is_admin = Column(Boolean, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    phone_number = Column(String(15), nullable=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    # created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # *Relationships*
    # Admin-user can organize many events
    events = relationship('Event', backref='user')
    # A user can make many bookings
    bookings = relationship('Booking', backref='user')
    
# Event model 
class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, nullable=False, primary_key=True) 
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    starts = Column(DateTime(timezone=True), nullable=False)
    event_ends = Column(DateTime(timezone=True), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    organizer_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # *Relationships*
    venue = relationship('Venue', backref='events')
    tickets = relationship('Ticket', backref='event')
    bookings = relationship('Booking', backref='event')
    category = relationship('Category', backref='events')

# Venue Model 
class Venue(Base):
    __tablename__ = 'venues'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(150), nullable=False)
    address = Column(String(250), nullable=True)
    city = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    capacity = Column(Integer, nullable=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

# Booking Model 
class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    ticket_id = Column(Integer, ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # *Relationships*
    ticket = relationship('Ticket', backref='bookings')

# Ticket Model 
class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(TicketType), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    booked = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

# Category Model 
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
