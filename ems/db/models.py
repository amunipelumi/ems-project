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

# Attendance model
# helps with the many to many relationship between users and events
class Attend(Base):
    __tablename__ = 'attends'
    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    # updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # *Relationship*
    # - Many-to-One with User (an attendee is one user)
    user = relationship('User', back_populates='attends')
    # - Many-to-One with Event (an attendee attends one event)
    event = relationship('Event', back_populates='attends')

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
    # - One-to-Many with Attend (a user can attend many events)
    attends = relationship('Attend', back_populates='user')
    # - One-to-Many with Ticket (a user can have many tickets)
    tickets = relationship('Ticket', back_populates='user')
    # - One-to-Many with Booking (a user can make many bookings)
    bookings = relationship('Booking', back_populates='user')
    # - One-to-Many with Event (a user can organize many events, as an admin)
    events_organized = relationship('Event', back_populates='event_organizer')

# Event model
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
    # - Many-to-One with Venue (an event is held at one venue)
    venue = relationship('Venue', back_populates='events')
    # - One-to-Many with Ticket (an event has many tickets)
    tickets = relationship('Ticket', back_populates='event')
    # - One-to-Many with Attend (an event has many attendees)
    attends = relationship('Attend', back_populates='event')
    # - One-to-Many with Booking (an event has many bookings)
    bookings = relationship('Booking', back_populates='event')
    # - Many-to-One with Category (an event belongs to one category)
    category = relationship('Category', back_populates='events')
    # - Many-to-One with User (an event is organized by one user)
    event_organizer = relationship('User', back_populates='events_organized')

# Ticket Model
class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(TicketType), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # *Relationships*
    # - Many-to-One with User (a user can have many tickets)
    user = relationship('User', back_populates='tickets')
    # - Many-to-One with Event (a ticket is for one event)
    event = relationship('Event', back_populates='tickets')
    # - One-to-Many with Booking (a ticket can be booked many times)
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

    # *Relationships*
    # - Many-to-One with User (a booking is made by one user)
    user = relationship('User', back_populates='bookings')
    # - Many-to-One with Event (a booking is for one event)
    event = relationship('Event', back_populates='bookings')
    # - Many-to-One with Ticket (a booking is for one ticket)
    ticket = relationship('Ticket', back_populates='bookings')

# Venue Model
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

    # *Relationships*
    # - One-to-Many with Event (a venue hosts many events)
    events = relationship('Event', back_populates='venue')

# Category Model
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # *Relationships*
    # - One-to-Many with Event (a category has many events)
    events = relationship('Event', back_populates='category')
