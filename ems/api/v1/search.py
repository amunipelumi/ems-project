###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional
from sqlalchemy import or_

###
from ...db import models, database
from ...core import oauth2
from ...__ import prefix_
from . import schemas



router = APIRouter(
    prefix=f'{prefix_}/search',
    tags=['Search']
)

# Search for events
@router.get('/', response_model=List[schemas.SearchEvents])
def search_events(
    skip: int=0,
    limit: int=10,
    search: Optional[str]="",
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user),
    ):
    ##
    category_col = ['name']
    category_ = [getattr(models.Category, col).ilike(f"%{search}%") for col in category_col]
    ##
    event_col = ['name', 'description']
    event_ = [getattr(models.Event, col).ilike(f"%{search}%") for col in event_col]
    ##
    venue_col = ['name', 'address', 'city', 'country']
    venue_ = [getattr(models.Venue, col).ilike(f"%{search}%") for col in venue_col]
    ##
    search_ = category_ + event_ + venue_
    events = (
        db.query(models.Event, models.Category, models.Venue)
        .join(models.Category)
        .join(models.Venue)
        .filter(or_(*search_))
        .limit(limit)
        .offset(skip)
        .all()
        )
    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No event was found!'
            )
    result = []
    for event in events:
        result.append(event._asdict())
    return result

# Search for event by id
@router.get('/{event_id}', response_model=schemas.SearchedEvent)
def search_event(
    event_id: int,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.current_user),
    ):
    ##
    event = db.query(models.Event).filter_by(
        id=event_id
        ).options(
            joinedload(models.Event.user),
            joinedload(models.Event.venue),
            joinedload(models.Event.tickets),
            joinedload(models.Event.category)
            ).first()
    ##
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Error!! No event found!'
            )
    ##
    event = event.__dict__
    organizer = event.pop('user')
    event['organizer'] = organizer
    return event
