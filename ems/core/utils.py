from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(pwd):
    return pwd_context.hash(pwd)

def verify(attempted_pwd, hashed_pwd):
    return pwd_context.verify(attempted_pwd, hashed_pwd)