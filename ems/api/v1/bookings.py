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
# GET /bookings/: List all bookings made by the user
# GET /bookings/{booking_id}: Get details of a specific booking
# PUT /bookings/{booking_id}: Update booking information
# DELETE /bookings/{booking_id}: Cancel a booking


# 1. Check for event availability
# 2. Check if ticket type is available and the number of it 
#    booked != quantity
# 3. Check if the number of tickets to be purchased does not
#    make booked exceed quantity
# 4. Check if they've booked the same ticket before and want to
#    book again 

# Book an event
@router.post('/events/{event_id}', response_model=schemas.Booked, status_code=201)
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
                joinedload(models.Event.user),
                joinedload(models.Event.venue),
                joinedload(models.Event.tickets),
                joinedload(models.Event.bookings),
                joinedload(models.Event.category)
                ).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail='Error, event was not found...'
                )
        # print(event.venue[0].__dict__)
        if event.organizer_id==auth_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You cannot book your own event..'
                )
        ##
        ticket = None
        tickets = event.tickets # A list of tickets
        # Check if the type of ticket exists
        exist = False
        for _ticket in tickets:
            if _ticket.type==ticket_.type:
                ticket = _ticket
                exist = True
                break
        if exist is not True:
            raise HTTPException(
                status_code=403, 
                detail=f'Chosen ticket is unavailable for this event..'
                )
        if ((ticket.booked + ticket_.quantity) > ticket.quantity):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Sorry, tickets fully booked...')
        # If they booked the same ticket previously, then update it
        booking_ = None
        bk_exist = False
        bookings = event.bookings # A list of bookings
        for _booking in bookings:
            if _booking.user_id==auth_user.id and \
            _booking.ticket_id==ticket.id:
                booking_ = _booking
                bk_exist = True
                break
        ##
        if bk_exist is not True:
            booking_ = {
                'user_id': auth_user.id,
                'event_id': event_id,
                'ticket_id': ticket.id,
                'quantity': ticket_.quantity
            }
            ##
            booking_ = models.Booking(**booking_)
            db.add(booking_)
            db.flush()
        else:
            # Update the current booking quantity
            booking_.quantity += ticket_.quantity

        ## Update the booked column of ticket
        ticket.booked += ticket_.quantity
        db.commit()
        db.refresh(booking_)
        print('Transaction successful...')
    ##
    except SQLAlchemyError as error:
        db.rollback()
        print(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Error occured while trying to book tickets...'
            )
    # event, category, venue, ticket, quantity
    response = {
        'event_date': event.starts,
        'event_name': event.name,
        'event_venue': event.venue[0].name,
        'event_description': event.description,
        'event_category': event.category.name,
        'event_organizer': event.user.name,
        'ticket_type': ticket_.type,
        'ticket_quantity': booking_.quantity
    }
    return response

# Get all user's bookings
@router.get('/')
def get_bookings(
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    bookings = db.query(models.Booking).filter_by(
        user_id=auth_user.id
        ).options(
            joinedload(models.Booking.event)
            ).all()
    if not bookings:
        raise HTTPException(
            status_code=404, 
            detail='You currently have no bookings'
            )
    ####_______________________________________
    for booking in bookings:
        print(booking.event.__dict__)
    ####_______________________________________
    pass
