###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError
from typing import List

###
from ...db import models, database
from ...core import oauth2
from ...__ import prefix_
from . import schemas



router = APIRouter(
    prefix=f'{prefix_}/bookings',
    tags=['Bookings']
)


# Booking Management
# POST /events/{event_id}/book: Book a ticket for a specific event
# GET /bookings/: List all bookings made by the user
# GET /bookings/{booking_id}: Get details of a specific booking
# PUT /bookings/{booking_id}: Update booking information
# DELETE /bookings/{booking_id}: Cancel a booking