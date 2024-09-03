# ###
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session

# ###
# import os
# import jwt
# from jose import JWTError
# from datetime import datetime, timedelta, timezone

# ###
# from ..api.v1 import schemas
# from ..db import database, models



# oauth_schema = OAuth2PasswordBearer('/login')

# EXPIRE_MIN = os.getenv('EXPIRE_MIN')
# SECRET_KEY = os.getenv('SECRET_KEY')
# ALGORITHM = os.getenv('ALGORITHM')


# def access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN)
#     to_encode.update({'exp': expire})
#     token = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
#     return token

# def verify_token(token: str, exception):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
#         username:str = payload.get('username')

#         if not username:
#             raise exception
        
#         token_data = schemas.TokenData(username=username)

#     except JWTError:
#         raise exception
    
#     return token_data
    
# def get_current_user(
#         token: str=Depends(oauth_schema), 
#         db: Session=Depends(database.get_db)
#         ):
    
#     exception = HTTPException(status.HTTP_401_UNAUTHORIZED, 
#                               'invalid credentials!!',
#                               {'WWW-Authenticate': 'Bearer'})
    
#     token_data = verify_token(token, exception)

#     user = (db.query(models.User)
#             .filter(models.User.username==token_data.username)
#             .first())
    
#     return user
