###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a new event
@router.post(
        '/',
        response_model=schemas.CreateEventResp,
        status_code=status.HTTP_201_CREATED 
        )
def create_event(
    evnt: schemas.CreateEventMain,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user),
    ):
    _category = evnt.category
    _ticket = evnt.tickets
    _venue = evnt.venue
    _event = evnt.event
    ##
    category = (
        db.query(models.Category)
        .filter_by(name=_category.name)
        .first()
        )
    if not category:
        category = models.Category(
            **_category.model_dump()
            )
        db.add(category)
        db.commit()
        db.refresh(category)
    ##
    venue = (
        db.query(models.Venue)
        .filter_by(
            name=_venue.name,
            city=_venue.city,
            address=_venue.address,
            country=_venue.country,
            capacity=_venue.capacity
            )
        .first()
        )
    if not venue:
        venue = models.Venue(
            **_venue.model_dump()
            )
        db.add(venue)
        db.commit()
        db.refresh(venue)
    ##
    event = (
        db.query(models.Event)
        .filter_by(
            name=_event.name,
            description=_event.description,
            starts=_event.starts,
            event_ends=_event.event_ends,
            organizer_id=auth_user.id,
            category_id=category.id,
            venue_id=venue.id
            )
        .first()
        )
    if not event:
        event_ = _event.model_dump()
        event_.update({
            'organizer_id': auth_user.id,
            'category_id': category.id,
            'venue_id': venue.id,
            })
        event = models.Event(**event_)
        db.add(event)
        db.commit()
        db.refresh(event)
    ##
    all_tickets = []
    for data in _ticket.tickets:
        ticket_ = data.model_dump()
        ticket_.update({
            'event_id': event.id
        })
        ticket = models.Ticket(**ticket_)
        all_tickets.append(ticket)
    db.add_all(all_tickets)
    db.commit()
    for _ in all_tickets:
        db.refresh(_)
    ##
    response = {
        'event': event,
        'venue': venue,
        'tickets': all_tickets,
        'organizer': auth_user,
        'category': category
        }
    return response 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get all events 
# with optional filters: by date, venue, category
@router.get(
        '/',
        response_model=List[schemas.GetEvent],
        )
def get_events(
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    events = (
        db.query(models.Event)
        .all()
        )
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No event found!')
    return events

# Get a specific event
@router.get(
        '/{id}', 
        response_model=schemas.GetEvent
        )
def get_event(
    id: int,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user)
    ):
    event = (
        db.query(models.Event)
        .filter(models.Event.id==id)
        .first()
        )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No event found!'
            )
    return event

# Update an event
@router.put(
        '/{id}',
        response_model=schemas.GetEvent,
        status_code=status.HTTP_202_ACCEPTED
        )
def update_event(
    id: int,
    event: schemas.EventTable,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    evt = (
        db.query(models.Event)
        .filter(
            models.Event.organizer_id==auth_user.id,
            models.Event.id==id
            )
        )
    if not evt.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Event not found!!'
            )
    event.organizer_id = auth_user.id
    evt.update(
        event.model_dump(), 
        synchronize_session=False
        )
    db.commit()
    _updated = evt.first()
    return _updated
    
# Delete an event
@router.delete(
        '/{id}',
        status_code=status.HTTP_204_NO_CONTENT
        )
def delete_event(
    id: int,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    evt = (
        db.query(models.Event)
        .filter(
            models.Event.organizer_id==auth_user.id,
            models.Event.id==id
            )
        )
    if not evt.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Event not found!!'
            )
    evt.delete(synchronize_session=False)
    db.commit()