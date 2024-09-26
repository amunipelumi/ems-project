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
    auth_user: dict=Depends(oauth2.current_user)
    ):
    ##
    try:
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
        ticket = None
        tickets = event.tickets
        # Check if the type of ticket exists
        exist = False
        for _ticket in tickets:
            if _ticket.type == ticket_.type:
                ticket = _ticket
                exist = True
                break
        if exist is not True:
            raise HTTPException(
                status_code=403, 
                detail=f'No "{ticket_.type}" ticket for this event..'
                )
        if ((ticket.booked + ticket_.quantity) > ticket.quantity):
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
        booking = models.Booking(**booking_)
        db.add(booking)
        db.flush()
        ## Update the booked column of ticket
        ticket.booked += ticket_.quantity
        db.commit()
        db.refresh(booking)
        print('Transaction successful...')
    ##
    except SQLAlchemyError as error:
        db.rollback()
        print(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Error occured while trying to book tickets...'
            )
    return booking
