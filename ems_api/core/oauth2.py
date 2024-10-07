###
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import EmailStr

###
import os
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone

###
from ..__ import prefix_
from ..api.v1 import schemas
from ..db import database, models



EXPIRE_DAYS = os.getenv('EXPIRE_DAYS')
EXPIRE_MIN = os.getenv('EXPIRE_MIN')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

oauth2_schema = OAuth2PasswordBearer(f'{prefix_}/auth/signin')

exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
    detail='Invalid credentials!!',
    headers={'WWW-Authenticate': 'Bearer'}
    )

# Generate jwt token using given data as payload
def get_token(data: dict, token_type: str):
    payload = data.copy()
    expire_min = (
        datetime.now(timezone.utc) + 
        timedelta(minutes=float(EXPIRE_MIN))
        )
    expire_days = (
        datetime.now(timezone.utc) + 
        timedelta(days=int(EXPIRE_DAYS))
        )
    if token_type == "access":
        payload.update({
            'exp': expire_min,
            'type': token_type
            })
    elif token_type == "refresh":
        payload.update({
            'exp': expire_days,
            'type': token_type
            })
    else: raise ValueError('Invalid token type...')
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
        type: str = payload.get('type')
        email: EmailStr = payload.get('email')
        is_admin: bool = payload.get('is_admin')
        if not email:
            raise exception
        _data = schemas.TokenData(
            type=type,
            email=email, 
            is_admin=is_admin
            )
    except InvalidTokenError:
        raise exception
    return _data

# Getting the current user, this becomes a vital dependency
# to be included on all path operation function where 
# authentication is required
def current_user(
        token: str=Depends(oauth2_schema), 
        db: Session=Depends(database.get_db)
        ):
    _data = verify_token(token)
    _user = (
        db.query(models.User)
        .filter(
            models.User.email==_data.email,
            )
        .first()
        )
    if _user:
        return _user
    raise exception

# Similar to current user but for admin, useful for operations
# requiring admin previledges (e.g: deleting an event)
def admin_user(
        token: str=Depends(oauth2_schema), 
        db: Session=Depends(database.get_db)
        ):
    _data = verify_token(token)
    _user = None
    if _data.is_admin:
        _user = (
            db.query(models.User)
            .filter(
                models.User.email==_data.email, 
                models.User.is_admin==_data.is_admin
                )
            .first()
            )
    if _user:
        return _user
    raise exception
