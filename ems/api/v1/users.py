###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

###
from ...db import models, database
from ...core import utils
from . import schemas



router = APIRouter(
    tags=['Users']
)

# Register/signup a new user
@router.post(
        '/signup', 
        response_model=schemas.GetUser, 
        status_code=status.HTTP_201_CREATED
        )
def create_user(
    user: schemas.CreateUser, 
    db: Session=Depends(database.get_db)
    ):
    user.password = utils.hash(user.password)
    _user = models.User(**user.model_dump())
    db.add(_user)
    db.commit()
    db.refresh(_user)
    return _user
    
# Get a user by id
@router.get(
        '/users/{id}', 
        response_model=schemas.GetUser
        )
def get_user(
    id: int, 
    db: Session=Depends(database.get_db)
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
    db: Session=Depends(database.get_db)
    ):
    users = db.query(models.User).all()
    if not users:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=f'No user found!!')
    return users
