###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

###
from ...db import models, database
from ...core import oauth2
from . import schemas



router = APIRouter(
    tags=['Users']
)

# Get a user by id
@router.get(
        '/users/{id}', 
        response_model=schemas.GetUser
        )
def get_user(
    id: int, 
    db: Session=Depends(database.get_db),
    __: dict=Depends(oauth2.current_user)
    ):
    user = db.query(models.User).filter(models.User.id==id).first()
    if not user:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=f'No user found!!')
    return user

# Get all users
@router.get(
    '/users', 
    response_model=List[schemas.GetUsers]
    )
def get_users(
    db: Session=Depends(database.get_db),
    __: dict=Depends(oauth2.current_user)
    ):
    # print(__.__dict__)
    users = db.query(models.User).all()
    if not users:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=f'No user found!!')
    return users
