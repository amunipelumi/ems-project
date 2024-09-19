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
    prefix=f'{prefix_}/events',
    tags=['Events']
)

# Create an event
@router.post('/', response_model=schemas.CreatedEvent, status_code=status.HTTP_201_CREATED)
def create_event(
    evnt: schemas.CreateEvent, 
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    ##
    _category = evnt.category
    _ticket = evnt.tickets
    _venue = evnt.venue
    _event = {
        'name': evnt.name,
        'description': evnt.description,
        'starts': evnt.starts,
        'event_ends': evnt.event_ends
    }
    ##
    try:
        category = db.query(models.Category).filter_by(
            name=_category.name
            ).first()
        if not category:
            category = models.Category(**_category.model_dump())
            db.add(category)
            db.flush()
        ##
        event = db.query(models.Event).filter_by(
            name=_event['name'],
            description=_event['description'],
            starts=_event['starts'],
            event_ends=_event['event_ends'],
            organizer_id=auth_user.id,
            category_id=category.id,
            ).first()
        if not event:
            _event['organizer_id'] = auth_user.id
            _event['category_id'] = category.id
            event = models.Event(**_event)
            db.add(event)
            db.flush()
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail='Sorry, this event already exists..')
        ##
        venue = _venue.model_dump()
        venue['event_id'] = event.id
        venue = models.Venue(**venue)
        db.add(venue)
        db.flush()
        ##
        all_tickets = []
        for data in _ticket.root:
            ticket = data.model_dump()
            ticket['event_id'] = event.id
            ticket = models.Ticket(**ticket)
            all_tickets.append(ticket)
        db.add_all(all_tickets)
        db.flush()
        ##
        db.commit()
        print("Transaction was successfull!")
    ##
    except SQLAlchemyError as error:
        db.rollback()
        print(error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail='Unable to create event at the moment...')
    ##
    response = {
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'starts': event.starts,
        'event_ends': event.event_ends,
        'venue': venue,
        'tickets': all_tickets,
        'organizer': auth_user,
        'category': category
    }
    return response

# Update an event
# @router.put('/{event_id}', response_model=schemas.CreatedEvent, status_code=status.HTTP_202_ACCEPTED)
# def update_event(
#     event_id: int,
#     evnt: schemas.CreateEvent,
#     db: Session=Depends(database.get_db),
#     auth_user: dict=Depends(oauth2.admin_user)
#     ):
#     ##
#     _category = evnt.category
#     _ticket = evnt.tickets
#     _venue = evnt.venue
#     _event = {
#         'name': evnt.name,
#         'description': evnt.description,
#         'starts': evnt.starts,
#         'event_ends': evnt.event_ends
#     }
#     ##
#     evt_query = db.query(models.Event).filter_by(id=event_id)
#     event = evt_query.first()
#     if not event:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail='Sorry, this event was not found...')
#     ##
#     try:
#         # change category 
#         category = db.query(models.Category).filter_by(
#             name=_category.name
#             ).first()
#         if not category:
#             category = models.Category(**_category.model_dump())
#             db.add(category)
#             db.flush()
#         # change venue
#         venue = db.query(models.Venue).filter_by(
#             name=_venue.name,
#             address=_venue.address,
#             city=_venue.city,
#             country=_venue.country,
#             capacity=_venue.capacity
#             )
#     ##
#     except SQLAlchemyError as error:
#         print(error)
#         db.rollback()
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
#                             detail='Unable to update event at the moment...')
#     ##
    # evnt.organizer_id = auth_user.id
    # evt.update(
    #     evnt.model_dump(), 
    #     synchronize_session=False
    #     )
    # db.commit()
    # _updated = evt.first()
    # return _updated

# Get all events (this is for admin)
# this will require pagination
@router.get('/', response_model=List[schemas.Events])
def get_events(
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    ##
    events = db.query(models.Event).filter_by(
        organizer_id=auth_user.id
        ).all()
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No event found!')
    return events

# Get a specific event (this is for admin)
@router.get('/{event_id}', response_model=schemas.EventDetails)
def get_event(event_id: int, 
              db: Session=Depends(database.get_db),
              auth_user: dict=Depends(oauth2.admin_user)):
    event = db.query(models.Event).filter_by(
        id=event_id, 
        organizer_id=auth_user.id
        ).options(
            joinedload(models.Event.venue),
            joinedload(models.Event.tickets),
            joinedload(models.Event.category)
            ).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No event found!'
            )
    event = event.__dict__
    # Include organizer to correspond with response schema
    event['organizer'] = auth_user
    return event
    
# Delete an event
@router.delete('/{event_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, 
                 db: Session=Depends(database.get_db),
                 auth_user: dict=Depends(oauth2.admin_user)):
    ##
    evt = db.query(models.Event).filter_by(
        id=event_id,
        organizer_id=auth_user.id
        )
    if not evt.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Event not found!!'
            )
    evt.delete(synchronize_session=False)
    db.commit()
