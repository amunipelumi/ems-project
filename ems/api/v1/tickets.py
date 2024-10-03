###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
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
    if not orders:
        raise HTTPException(
            status_code=404,
            detail='You currently have no orders...'
            )
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

@router.get('/{order_id}', response_model=schemas.OrderDetail)
def my_ticket(
    order_id: int,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    ##
    order = (db.query(models.Booking, models.Ticket, models.Event, models.User, models.Venue)
             .join(models.Ticket, models.Booking.ticket_id==models.Ticket.id)
             .join(models.Event, models.Ticket.event_id==models.Event.id)
             .join(models.User, models.Event.organizer_id==models.User.id)
             .join(models.Venue)
             .filter(models.Booking.id==order_id, models.Booking.user_id==auth_user.id)
             .first()
            )
    if not order:
        raise HTTPException(
            status_code=404,
            detail='Order not found...'
            )
    # tickets = [n._asdict() for n in order]
    res = {
        'name': order.Event.name,
        'date': order.Event.starts,
        'location': order.Venue.name,
        'organizer': order.User.name,
        'ticket_type': order.Ticket.type,
        'attendee': auth_user
    }
    return res
