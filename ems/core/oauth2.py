###
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import EmailStr

###
import os
import jwt
# from jwt import exceptions
# from jose import JWTError
from datetime import datetime, timedelta, timezone

###
from ..api.v1 import schemas
from ..db import database, models



EXPIRE_MIN = os.getenv('EXPIRE_MIN')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

oauth2_schema = OAuth2PasswordBearer('/signin')

exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
    detail='Invalid credentials!!',
    headers={'WWW-Authenticate': 'Bearer'}
    )

# Generate jwt token using given data as payload
def get_token(data: dict):
    payload = data.copy()
    expire_min = (
        datetime.now(timezone.utc) + 
        timedelta(minutes=float(EXPIRE_MIN))
        )
    payload.update({'exp': expire_min})
    token = jwt.encode(
        payload, 
        key=SECRET_KEY, 
        algorithm=ALGORITHM
        )
    return token

# Verify a given token 
def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, 
            key=SECRET_KEY, 
            algorithms=[ALGORITHM]
            )
        email: EmailStr = payload.get('email')
        if not email:
            raise exception
        token_data = schemas.TokenData(email=email)
    except jwt.exceptions:
        raise exception
    return token_data

# Getting the current user, this becomes a vital dependency
def current_user(
        token: str=Depends(oauth2_schema), 
        db: Session=Depends(database.get_db)
        ):
    token_data = verify_token(token)
    _user = (
        db.query(models.User)
        .filter(models.User.email==token_data.email)
        .first()
        )
    return _user
