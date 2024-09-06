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

# Create a new event
@router.post('/')
def create_event():
    pass

# Get all events 
# with optional filters: by date, venue, category
@router.get('/')
def get_events():
    pass

# Get a specific event
@router.get('/{id}')
def get_event():
    pass

# Update an event
@router.put('/{id}')
def update_event():
    pass

# Delete an event
@router.delete('/{id}')
def delete_event():
    pass