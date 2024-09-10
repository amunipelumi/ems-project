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
    prefix=f'{prefix_}/tickets',
    tags=['Tickets']
    )

# DELETE /tickets/{ticket_id}: Delete a ticket

# Create a ticket for an event (admins only)
# id here is event id
@router.post(
    '/events/{id}/',
    response_model=schemas.GetTickets,
    status_code=status.HTTP_201_CREATED
    )
def create_ticket(
    id: int,
    ticket: schemas.CreateTicket, 
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    # search for the event
    evt = (
        db.query(models.Event)
        .filter(
            models.Event.id==id, 
            models.Event.organizer==auth_user.id
            )
        .first()
        )
    if not evt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Event not found!'
            )
    ticket.owner = auth_user.id
    nt = models.Ticket(**ticket.model_dump())
    db.add(nt)
    db.commit()
    db.refresh(nt)
    return nt 

# Get all tickets for an event
# id here is event id
@router.get(
    '/events/{id}',
    response_model=List[schemas.GetTickets]
    )
def get_ticket(
    id: int,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    evt = (
        db.query(models.Event)
        .filter(
            models.Event.id==id, 
            models.Event.organizer==auth_user.id
            )
        .first()
        )
    if not evt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Event not found!'
            )
    tickets = (
        db.query(models.Ticket)
        .filter_by(event=evt.id)
        .all()
        )
    if not tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='No ticket found'
            )
    return tickets

# Update ticket details
# id here is ticket id
@router.put(
        '/{id}',
        response_model=schemas.GetTickets,
        status_code=status.HTTP_202_ACCEPTED)
def update_ticket(
    id: int,
    tckt: schemas.CreateTicket,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    ticket = (
        db.query(models.Ticket)
        .filter_by(id=id, owner=auth_user.id)
        )
    if not ticket.first():
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='Ticket not found!'
            )
    tckt.owner = auth_user.id
    ticket.update(
        tckt.model_dump(),
        synchronize_session=False
        )
    db.commit()
    _updated = ticket.first()
    return _updated

# Delete a ticket
# id here is ticket id
@router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT
    )
def delete_ticket(
    id: int,
    db: Session=Depends(database.get_db),
    auth_user: dict=Depends(oauth2.admin_user)
    ):
    ticket = (
        db.query(models.Ticket)
        .filter_by(id=id, owner=auth_user.id)
        )
    if not ticket.first():
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='Ticket not found!'
            )
    ticket.delete(synchronize_session=False)
    db.commit()