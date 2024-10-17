from passlib.context import CryptContext
from sqlalchemy.orm import class_mapper
from bson import ObjectId
import enum



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(pwd):
    '''
    Function to hash a given password.
    '''
    return pwd_context.hash(pwd)

def verify(attempted_pwd, hashed_pwd):
    '''
    Verifies if an attempted password hash matches original password hash.
    '''
    return pwd_context.verify(attempted_pwd, hashed_pwd)

def to_dict(obj, recurse=False):
    """
    This helps to converts a SQLAlchemy model instance to a Python dictionary.\n
    Set *recurse=True* if query has relationships.
    """
    # Handling enum in ticket
    def handle_enum(data):
        if isinstance(data, enum.Enum):
            return data.value
        elif isinstance(data, ObjectId):
            return str(data)
        return data
    ##
    if not recurse:
        return {c.name: handle_enum(getattr(obj, c.name)) for c in obj.__table__.columns}
    ##
    else:
        columns = {c.key: handle_enum(getattr(obj, c.key)) for c in class_mapper(obj.__class__).columns}
        for rel in class_mapper(obj.__class__).relationships:
            rel_obj = getattr(obj, rel.key)
            ##
            if rel_obj is None:
                columns[rel.key] = None
            ##
            elif rel.uselist:  
                columns[rel.key] = [to_dict(child) for child in rel_obj]
            ##
            else:  
                columns[rel.key] = to_dict(rel_obj)
        ##
        return columns
