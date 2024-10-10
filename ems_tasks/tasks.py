##
from sqlalchemy.orm import Session

##
from ems_api.db import database, models
from ems_api.core import config
from .celery import app

##
import pickle


@app.task
def recache_events(auth_user):
    """
    Re-cache events for user after an event update.
    """
    cache = config.redis_client()
    db: Session=next(database.get_db())
    key = f'{auth_user.username}_events'
    ##
    events = db.query(models.Event).filter_by(
        organizer_id=auth_user.id
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
def recache_event(event_id, auth_user):
    """
    Re-cache a specific event for user after an event update.
    """
    cache = config.redis_client()
    db: Session=next(database.get_db())
    key = f'{auth_user.username}_event_{event_id}'
    ##
    event = db.query(models.Event).filter_by(
        id=event_id,
        organizer_id=auth_user.id
        ).first()
    ##
    if event:
        cache.set(key, pickle.dumps(event), ex=86400)
        return {
            "Status": f"Successfully re-cached event {event_id}.",
            }
    else:
        return {
            "Status": "Unsuccessful..", 
            "Message": "No event to re-cache.."
            }