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
# POST /events/{event_id}/tickets: Create tickets for an event
# GET /events/{event_id}/tickets: List all tickets for a specific event
# GET /tickets/{ticket_id}: Get details of a specific ticket
# PUT /tickets/{ticket_id}: Update ticket information
# DELETE /tickets/{ticket_id}: Delete a ticket