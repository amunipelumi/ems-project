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
    prefix=f'{prefix_}/tickets',
    tags=['Tickets']
)

# Ticket Management
# GET /events/{event_id}: List all tickets for a specific event
# GET /{ticket_id}: Get details of a specific ticket
# PUT /{ticket_id}: Update ticket information
# DELETE /{ticket_id}: Delete a ticket