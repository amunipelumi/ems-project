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

    # Relationships
    bookings = relationship('Booking', back_populates='user')
    events = relationship('Event', back_populates='user')

# Event model
class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, nullable=False, primary_key=True) 
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    starts = Column(DateTime(timezone=True), nullable=False)
    event_ends = Column(DateTime(timezone=True), nullable=False)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    organizer = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='events')
    venue = relationship('Venue', back_populates='events')
    tickets = relationship('Ticket', back_populates='event')
    bookings = relationship('Booking', back_populates='event')
    category = relationship('Category', back_populates='events')

# Ticket Model
class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(TicketType), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    event = relationship('Event', back_populates='tickets')
    bookings = relationship('Booking', back_populates='ticket')

# Booking Model
class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationships
    user = relationship('User', back_populates='bookings')
    event = relationship('Event', back_populates='bookings')
    ticket = relationship('Ticket', back_populates='bookings')

# Venue Model
class Venue(Base):
    __tablename__ = 'venues'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(150), nullable=False)
    address = Column(String(250), nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    events = relationship('Event', back_populates='venue')

# Category Model
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    events = relationship('Event', back_populates='category')

# Search Model (for storing search history or queries)
class Search(Base):
    __tablename__ = 'searches'

    id = Column(Integer, primary_key=True)
    query = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    user = relationship('User')
