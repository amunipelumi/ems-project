###
from fastapi import status, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm as opr
from sqlalchemy.orm import Session

###
from ...db import models, database
from ...core import utils, oauth2
from . import schemas



router = APIRouter(
    tags=['Authentication']
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

# Login/signin a user
@router.post(
        '/signin',
        response_model=schemas.Token
        )
def login(
    user: opr=Depends(),
    # user: schemas.LoginUser,
    db: Session=Depends(database.get_db)
    ):
    # Check for user
    db_query = (
        db.query(models.User)
        .filter(models.User.email==user.username)  # user.email)
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
    token = oauth2.get_token({'email': user.username})
    return {'access_token': token, 'token_type': 'bearer'}
    