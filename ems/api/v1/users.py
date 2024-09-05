###
from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

###
from ...db import models, database
from ...core import oauth2
from . import schemas



router = APIRouter(
    prefix='/users',
    tags=['Users']
)

## Handling currently logged in user
# Get current user profile/account
@router.get(
        '/me',
        response_model=schemas.User
        )
def get_me(
    me: dict=Depends(oauth2.current_user)
    ):
    # print(me.__dict__)
    return me

# Update current user profile/account
@router.put(
        '/me',
        response_model=schemas.User,
        status_code=status.HTTP_202_ACCEPTED,
        )
def update_me(
    __: schemas.User,
    db: Session=Depends(database.get_db),
    me: dict=Depends(oauth2.current_user),
    ):
    db_query = (
        db.query(models.User)
        .filter(models.User.email==me.email)
        )
    # This is highly unlikely because you'd be logged in
    # _own = db_query.first()
    # if not _own:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail='User not found!!')
    try:
        db_query.update(__.model_dump(), synchronize_session=False)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Details already in use'
            )
    # Make a new db request and return the updated details
    _updated = (
        db.query(models.User)
        .filter(models.User.email==__.email)
        .first()
        )
    return _updated

# Delete current user profile/account
@router.delete(
        '/me',
        status_code=status.HTTP_204_NO_CONTENT
        )
def delete_me(
    me: dict=Depends(oauth2.current_user),
    db: Session=Depends(database.get_db)
    ):
    db_query = (
        db.query(models.User)
        .filter(models.User.email==me.email)
        )
    # This is highly unlikely because you'd be logged in
    # _own = db_query.first()
    # if not _own:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail='User not found!!')
    db_query.delete(synchronize_session=False)
    db.commit()
    return {'detail': 'Account successfully deleted!'}

# Get a user by id
@router.get(
        '/{id}', 
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

# # Get all users
# @router.get(
#     '/all', 
#     response_model=List[schemas.GetUsers]
#     )
# def get_users(
#     db: Session=Depends(database.get_db),
#     __: dict=Depends(oauth2.current_user)
#     ):
#     # print(__.__dict__)
#     users = db.query(models.User).all()
#     if not users:
#        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                            detail=f'No user found!!')
#     return users
