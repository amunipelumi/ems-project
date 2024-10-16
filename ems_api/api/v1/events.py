###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List

###
from ...tasks.tasks import recache_events, recache_event
from ...core import oauth2, config, utils
from ...db import models, database
from ...__ import prefix_
from . import schemas

##
import pickle
import time



router = APIRouter(
    prefix=f'{prefix_}/events',
    tags=['Events']
)

# image, event_title, brief_des, date_time, location, about_event, tags/categories, organizer

# Create an event
@router.post('/', response_model=schemas.CreatedEvent, 
             status_code=status.HTTP_201_CREATED)
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail='Sorry, this event already exists..'
                )
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
        # print("\n**Transaction was successfull**\n")
    ##
    except SQLAlchemyError as error:
        db.rollback()
        print(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Unable to create event at the moment...'
            )
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
@router.put('/{event_id}', response_model=schemas.CreatedEvent, 
            status_code=status.HTTP_202_ACCEPTED)
def update_event(
    event_id: int,
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
    event = db.query(models.Event).filter_by(
        id=event_id
        ).options(
            joinedload(models.Event.venue),
            joinedload(models.Event.tickets)
            ).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Sorry, this event was not found...'
            )
    ##
    try:
        ## 
        category = db.query(models.Category).filter_by(
            name=_category.name
            ).first()
        if not category:
            category = models.Category(**_category.model_dump())
            db.add(category)
            db.flush()
        ##
        venue = event.venue[0]
        venue_ = _venue.model_dump()
        for x, y in venue_.items():
            setattr(venue, x, y)
        db.flush()
        ##
        tickets = event.tickets
        if len(tickets) != len(_ticket.root):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='There was an error in the number of tickets..'
                )
        num = 0
        for ticket in tickets:
            ticket_ = _ticket.root[num]
            ticket_ = ticket_.model_dump()
            for x, y in ticket_.items():
                setattr(ticket, x, y)
            num += 1
        db.flush()
        ##
        _event['category_id'] = category.id
        for x, y in _event.items():
            setattr(event, x, y)
        db.flush()
        ##
        db.commit()
        # print("\n**Transaction was successfull**\n")
    ##
    except SQLAlchemyError as error:
        print(error)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Unable to update event at the moment...'
            )
    ##
    response = {
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'starts': event.starts,
        'event_ends': event.event_ends,
        'venue': venue,
        'tickets': tickets,
        'organizer': auth_user,
        'category': category
    }
    # Run celery tasks to re-cache
    user_id = auth_user.id
    username = auth_user.username
    recache_events.delay(user_id, username)
    recache_event.delay(user_id, username, event_id)
    return response

# Get all events (this is for admin)
# this will require pagination
@router.get('/', response_model=List[schemas.Events])
def get_events(
    cache=Depends(config.redis_client),
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    # start_time = time.time()
    key = f'{auth_user.username}_events'
    events = cache.get(key)
    ##
    if events is None:
        events = db.query(models.Event).filter_by(
            organizer_id=auth_user.id
            ).all()
        if not events:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No event found!'
                )
        cache.set(key, pickle.dumps(events), 86400)
        # print(time.time() - start_time)
        return events
    ##
    events = pickle.loads(events)
    # print(time.time() - start_time)
    return events

# Get a specific event (this is for admin)
@router.get('/{event_id}', response_model=schemas.EventDetails)
def get_event(
    event_id: int, 
    cache=Depends(config.redis_client),
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    # start_time = time.time()
    ##
    key = f'{auth_user.username}_event_{event_id}'
    event = cache.get(key)
    ##
    if event is None:
        event = db.query(models.Event).filter_by(
            id=event_id, 
            organizer_id=auth_user.id
            ).options(
                joinedload(models.Event.venue),
                joinedload(models.Event.tickets),
                joinedload(models.Event.category)
                ).first()
        ##
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No event found!'
                )
        ##
        event = utils.to_dict(event, recurse=True)
        # Include organizer to correspond with response schema
        event['organizer'] = event.pop('user')
        cache.set(key, pickle.dumps(event), 86400)
        # print(time.time() - start_time)
        return event
    ##
    event = pickle.loads(event) 
    # print(time.time() - start_time)
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
