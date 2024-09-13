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
    evnt: schemas.EventTable,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user),
    ):
    event = evnt.model_copy(update={'organizer_id': auth_user.id})
    _event = models.Event(**event.model_dump())
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