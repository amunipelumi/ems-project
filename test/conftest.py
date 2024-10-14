##
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

##
from ems_api.db.database import Base, get_db
from ems_api.api.v1 import schemas
from ems_api.db import models
from ems_api.main import app
from ems_api.__ import prefix_

##
from dotenv import load_dotenv
import pytest
import os



load_dotenv()

DB_USERNAME = os.getenv('DB_USERNAME')
DB_HOSTNAME = os.getenv('DB_HOSTNAME')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DATABASE_URL = (f'postgresql://{DB_USERNAME}:{DB_PASS}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}-test')

Engine = create_engine(DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

admin_user = {
    'name': 'Admin User',
    'username': 'admin',
    'email': 'admin@email.com',
    'password': 'Password12345'
}
##
user = {
    'name': 'User',
    'username': 'user',
    'email': 'user@email.com',
    'password': 'Password1234'
}

@pytest.fixture()
def session_client():
    '''
    This should yield a FastAPI TestClient with database dependency overwritten.
    '''
    print('TestClient fixture..')
    # Base.metadata.drop_all(bind=Engine)
    Base.metadata.create_all(bind=Engine)
    db = TestSessionLocal()
    def get_db2():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = get_db2
    yield TestClient(app)

@pytest.fixture()
def test_user_reg(session_client):
    '''
    Registering users, both admin and normal user for testing..
    '''
    ##
    admin_url = f'{prefix_}/auth/signup/admin_user'
    admin_res = session_client.post(admin_url, json=admin_user)
    assert admin_res.status_code==201
    admin_data = schemas.GetAdmin(**admin_res.json())
    admin_data.password = admin_user.password
    assert admin_data.is_admin==True
    ##
    user_url = f'{prefix_}/auth/signup'
    user_res = session_client.post(user_url, json=user)
    assert user_res.status_code==201
    user_data = schemas.GetUser(**user_res.json())
    user_data.password = user.password
    ##
    print(admin_data, user_data)
    return admin_data, user_data

# @pytest.fixture()
# def test_user_login(test_user_reg):
#     pass    