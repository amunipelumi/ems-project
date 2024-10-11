##
from sqlalchemy.orm import Session, joinedload

##
from ems_api.db import database, models
from ems_api.core import config
from ems_api.celery import app

##
import pickle


@app.task
def recache_events(user_id: int, username: str):
    """
    Re-cache events for user after an event update.
    """
    cache = config.redis_client()
    db: Session=next(database.get_db())
    key = f'{username}_events'
    ##
    events = db.query(models.Event).filter_by(
        organizer_id=user_id
        ).all()
    ##
    if events:
        cache.set(key, pickle.dumps(events), ex=86400)
        return {
            "Status": "Successfully re-cached..",
            "Events": len(events)
            }
    else:
        return {
            "Status": "Unsuccessful..", 
            "Message": "No event to re-cache.."
            }

@app.task
def recache_event(user_id: int, username: str, event_id: int):
    """
    Re-cache a specific event for user after an event update.
    """
    cache = config.redis_client()
    db: Session=next(database.get_db())
    key = f'{username}_event_{event_id}'
    ##
    event = db.query(models.Event).filter_by(
        id=event_id,
        organizer_id=user_id
        ).options(
            joinedload(models.Event.venue),
            joinedload(models.Event.tickets),
            joinedload(models.Event.category)
            ).first()
    ##
    if event:
        cache.set(key, pickle.dumps(event), ex=86400)
        return {
            "Status": f"Successfully re-cached event id_{event_id}.",
            }
    else:
        return {
            "Status": "Unsuccessful..", 
            "Message": "No event to re-cache.."
            }