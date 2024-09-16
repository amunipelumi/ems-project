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
        response_model=schemas.GetEvent,
        status_code=status.HTTP_201_CREATED 
        )
def create_event(
    evnt: schemas.CreateEventMain,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user),
    ):
    category = evnt.category
    venue = evnt.venue
    event = evnt.event
    _category = (
        db.query(models.Category)
        .filter_by(name=category.name)
        .first()
        )
    if not _category:
        _category = models.Category(
            **category.model_dump()
            )
        db.add(_category)
        db.commit()
        db.refresh(_category)
    _venue = (
        db.query(models.Venue)
        .filter_by(
            name=venue.name,
            city=venue.city,
            address=venue.address,
            country=venue.country,
            capacity=venue.capacity
            )
        .first()
        )
    if not _venue:
        _venue = models.Venue(
            **venue.model_dump()
            )
        db.add(_venue)
        db.commit()
        db.refresh(_venue)
    _event = (
        db.query(models.Event)
        .filter_by(
            name=event.name,
            description=event.description,
            starts=event.starts,
            event_ends=event.event_ends,
            organizer_id=auth_user.id,
            category_id=_category.id,
            venue_id=_venue.id
            )
        .first()
        )
    if not _event:
        event_ = event.model_dump()
        event_.update({
            'organizer_id': auth_user.id,
            'category_id': _category.id,
            'venue_id': _venue.id,
            })
        _event = models.Event(**event_)
        db.add(_event)
        db.commit()
        db.refresh(_event)
    return _event
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