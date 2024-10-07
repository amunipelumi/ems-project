###
from fastapi import status, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm as opr
from sqlalchemy.orm import Session

###
from ...db import models, database
from ...core import utils, oauth2
from ...__ import prefix_
from . import schemas



router = APIRouter(
    prefix=f'{prefix_}/auth',
    tags=['Authentication'],
)

# Create an admin user
# This user can create events for others to attend
@router.post(
        '/signup/admin_user', 
        response_model=schemas.GetAdmin, 
        status_code=status.HTTP_201_CREATED
        )
def create_admin(
    user: schemas.CreateAdmin, 
    db: Session=Depends(database.get_db)
    ):
    user.password = utils.hash(user.password)
    _user = models.User(**user.model_dump())
    try:
        db.add(_user)
        db.commit()
        db.refresh(_user)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Details already in use'
            )
    return _user

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
    try:
        db.add(_user)
        db.commit()
        db.refresh(_user)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Details already in use'
            )
    return _user

# Login/signin a user
@router.post(
        '/signin',
        response_model=schemas.LoginRes
        )
def login(
    user: opr=Depends(),
    # user: schemas.LoginUser,
    db: Session=Depends(database.get_db)
    ):
    # Check for user depending on the schema used
    # user.username or user.email
    db_query = (
        db.query(models.User)
        .filter(models.User.email==user.username)
        .first()
        )
    if not db_query:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Invalid credentials'
            )
    # Check password validity
    pwd = utils.verify(user.password, db_query.password)
    if not pwd:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid credentials'
        )
    # Create and return access token
    data = {
        'is_admin': db_query.is_admin,
        'email': user.username
        }
    access_token = oauth2.get_token(data, 'access')
    refresh_token = oauth2.get_token(data, 'refresh')
    return {
        'token_type': 'bearer',
        'access_token': access_token,
        'refresh_token': refresh_token
        }

# Refresh token
@router.post(
        '/refresh', 
        response_model=schemas.AccessToken
        )
def refresh_token(
    body: schemas.Refresh
    ):
    token = body.token
    # Verify token
    _data = oauth2.verify_token(token)
    if _data.type != 'refresh':
        raise HTTPException(
            status_code=401,
            detail='Session expired, please login to continue...'
            )
    # Get and return new access token
    data = _data.model_dump()
    access_token = oauth2.get_token(data, 'access')
    return {'access_token': access_token, 'token_type': 'bearer'}
