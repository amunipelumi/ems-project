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
    # EARLY_BIRD = "Early Bird"

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
    # A user can organize many events as an admin
    events = relationship('Event', backref='user')
    # A user can make many bookings
    bookings = relationship('Booking', backref='user')
    
# Event model **admin
class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, nullable=False, primary_key=True) 
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    starts = Column(DateTime(timezone=True), nullable=False)
    event_ends = Column(DateTime(timezone=True), nullable=False)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    organizer_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # *Relationships*
    # An event is held at one venue
    venue = relationship('Venue', backref='events')
    # An event has many tickets
    tickets = relationship('Ticket', backref='event')
    # An event has many bookings
    bookings = relationship('Booking', backref='event')
    # An event belongs to one category
    category = relationship('Category', backref='events')

# Venue Model **independent
class Venue(Base):
    __tablename__ = 'venues'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(150), nullable=False)
    address = Column(String(250), nullable=False, unique=True)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

# Booking Model **non-admin user
class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # *Relationships*
    ticket = relationship('Ticket', backref='bookings')

# Ticket Model **admin
class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(TicketType), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

# Category Model **independent
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
