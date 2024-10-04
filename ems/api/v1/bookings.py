###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

###
from ...db import models, database
from ...core import oauth2
from ...__ import prefix_
from . import schemas



router = APIRouter(
    prefix=f'{prefix_}/bookings',
    tags=['Bookings']
)

# 1. Check for event availability
# 2. Check if ticket type is available and the number of it 
#    booked != quantity
# 3. Check if the number of tickets to be purchased does not
#    make booked exceed quantity
# 4. Check if they've booked the same ticket before and want to
#    book again 

# Book an event
@router.post('/events/{event_id}', response_model=schemas.Ordered, status_code=201)
def book_event(
    event_id: int,
    ticket_: schemas.Order,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    ##
    try:
        event = db.query(models.Event).filter_by(
            id=event_id
            ).options(
                joinedload(models.Event.venue),
                joinedload(models.Event.tickets),
                joinedload(models.Event.bookings),
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
        # print('Transaction successful...')
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
        'attendee': auth_user.email,
        'event_name': event.name,
        'event_date': event.starts,
        'event_venue': event.venue[0].name
    }
    return response

# Update order
@router.put('/{order_id}', status_code=202)
def update_booking(
    order_id: int,
    order: schemas.OrderUpdate,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    new_ticket_type = order.type # new type
    new_order_quantity = order.quantity # new quantity
    ##
    order_ = db.query(models.Booking).filter_by(
        id=order_id,
        user_id=auth_user.id
        ).options(
            joinedload(models.Booking.ticket)
            ).first()
    if not order_:
        raise HTTPException(
            status_code=404,
            detail='Your booking for this event was not found'
            )
    ##
    # Change the quantity
    former_order_quantity = order_.quantity
    total_ticket_quantity = order_.ticket.quantity
    total_ticket_booked = order_.ticket.booked
    ##
    try:
        if (((total_ticket_booked - former_order_quantity) + 
             new_order_quantity) > 
             total_ticket_quantity):
            raise HTTPException(
                status_code=403,
                detail='Sorry tickets fully booked...'
                )
        ##
        order_.quantity = new_order_quantity
        order_.ticket.booked = (order_.ticket.booked - former_order_quantity) + new_order_quantity
        db.commit()
        db.refresh(order_)
    ##
    except SQLAlchemyError as error:
        print(error)
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail='Unable to update order at this time...'
            )
    return {'detail': 'Order successfully updated...'}

# Delete ticket or cancel order
@router.delete('/{order_id}', status_code=204)
def delete_booking(
    order_id: int,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    ##
    order_ = db.query(models.Booking).filter_by(
        id=order_id,
        user_id=auth_user.id
        ).options(
            joinedload(models.Booking.ticket)
            ).first()
    if not order_:
        raise HTTPException(
            status_code=404,
            detail='Your booking for this event was not found'
            )
    ##
    try:
        former_order_quantity = order_.quantity
        order_.ticket.booked = (order_.ticket.booked - former_order_quantity)
        db.delete(order_)
        db.commit()
    ##
    except SQLAlchemyError as error:
        print(error)
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail='Sorry, operation was unsuccessful...'
            )
