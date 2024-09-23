###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from sqlalchemy import or_
from typing import List, Optional

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
@router.get('/', )# response_model=List[schemas.Events])
def search_event(
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
    # events = (
    #     db.query(models.Event)
    #     .options(
    #         joinedload(models.Event.category), 
    #         joinedload(models.Event.venue)
    #         )
    #     .filter(or_(*search_))
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    #     )
    events = (
    db.query(models.Event)
    .join(models.Venue) 
    .join(models.Category)
    .filter(or_(*search_)) 
    .limit(limit)
    .offset(skip)
    .all())
    
    print(events.__dict__)
    # return events


# @router.get('/', response_model=List[schemas.PostResponse2])
# def get_all_posts(
#     db: Session=Depends(database.get_db), 
#     user_data: str=Depends(oauth2.get_current_user), 
#     search: Optional[str]="", limit: int=10, skip: int=0
#     ):
    
#     # owner_all = (db.query(models.Post)
#     #              .filter(models.Post.user_id==user_data.id, 
#     #                      models.Post.title.contains(search))
#     #              .limit(limit).offset(skip).all())

#     owner_all = (db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
#                 .join(models.Vote, models.Vote.post_id==models.Post.id, isouter=True)
#                 .group_by(models.Post.id)
#                 .filter(models.Post.title.contains(search))
#                 .limit(limit)
#                 .offset(skip)
#                 .all())