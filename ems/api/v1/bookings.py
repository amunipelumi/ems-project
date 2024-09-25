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


# 1. Check for event availability
# 2. Check if ticket type is available and the number of it 
#    booked != quantity
# 3. Check if the number of tickets to be purchased does not
#    make booked exceed quantity

# Book an event
@router.post('/{event_id}')
def book_event(
    event_id: int,
    ticket_: schemas.Book,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    ##
    event = db.query(models.Event).filter_by(
        id=event_id
        ).options(
            joinedload(models.Event.tickets)
            ).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Error, event was not found...'
            )
    ##
    _type = None
    tickets = event.tickets
    # Check if the type of ticket exists
    exist = False
    for ticket in tickets:
        if ticket['type'] == ticket_.type:
            _type = ticket
            exist = True
            break
    if exist is not True:
        raise HTTPException(
            status_code=403, 
            detail=f'No "{ticket_.type}" ticket for this event..'
            )
    if ((_type.booked + ticket_.quantity) > _type.quantity):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Sorry, tickets fully booked...')
    ##
    booking_ = {
        'user_id': auth_user.id,
        'event_id': event_id,
        'ticket_id': ticket.id,
        'quantity': ticket_.quantity
    }
    ##
    try:
        booking = models.Booking(**booking_)
        db.add(booking)
        db.flush()
        ## Update the booked column of ticket
        ticket = db.query(models.Ticket).filter_by(event_id=event_id, type=_type.type).first()
    except SQLAlchemyError as error:
        db.rollback()
        print(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Error occured...'
            )
    return booking


# user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
#     event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
#     ticket_id = Column(Integer, ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
#     quantity = Column(Integer, nullable=False)