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

# GET /{ticket_id}: Get details of a specific ticket
# PUT /{ticket_id}: Update ticket information
# DELETE /{ticket_id}: Delete a ticket

# Event name
# Ticket type 
# Full address
# Date and time 

# Get all booked tickets
@router.get('/', response_model=List[schemas.AllOrders])
def my_tickets(
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    ##
    orders = db.query(models.Booking).filter_by(
        user_id=auth_user.id
        ).options(
            joinedload(models.Booking.event),
            joinedload(models.Booking.ticket)
            ).all()
    ##
    all_tickets = []
    for order in orders:
        res = {}
        res['order_id'] = order.id
        res['name'] = order.event.name
        res['date'] = order.event.starts
        res['ticket'] = order.ticket.type
        all_tickets.append(res)
    return all_tickets

# get specific comes with image, name, date, location, organizer, ticket_type, attendee(name, email, etc)
@router.get('/{order_id}')
def my_ticket(
    order_id: int,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    ##
    order = (db.query(models.Booking, models.Ticket, models.Event, models.Venue)
             .join(models.Ticket, models.Booking.ticket_id==models.Ticket.id)
             .join(models.Event, models.Ticket.event_id==models.Event.id)
             .join(models.Venue)
             .filter(models.Booking.id==order_id)
             .first()
            )
    ##________________________________________________
    print(order.Booking.__dict__)
    # print(order[0]._asdict())
    # for _ in order:
    #     print(_._asdict)
    ##________________________________________________
