##
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

##
from ems_api.db.database import Base, get_db
from ems_api.api.v1 import schemas
from ems_api.core import oauth2
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

user = {
    'name': 'User',
    'username': 'user',
    'email': 'user@email.com',
    'password': 'Password1234'
}

event = {
    "name": "Create test event",
    "description": "This event is for testing purpose",
    "starts": "2024-10-30T14:00:00+01:00",
    "category": {
        "name": "Test"
    },
    "venue": {
        "name": "Hall 55",
        "address": "Road 66",
        "city": "City 77",
        "country": "Country 88",
        "capacity": 99
    },
    "tickets": [
        {
            "type": "Regular",
            "price": 15.0,
            "quantity": 150,
        }
    ]
}

def get_db2():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

@pytest.fixture()
def session_client():
    '''
    This would yield a FastAPI TestClient with database dependency overwritten.
    '''
    # print('TestClient fixture..')
    Base.metadata.drop_all(bind=Engine)
    Base.metadata.create_all(bind=Engine)
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
    admin_model = schemas.GetAdmin(**admin_res.json())
    admin_data = admin_model.model_dump()
    admin_data['password'] = admin_user['password']
    assert admin_data['is_admin']==True
    ##
    user_url = f'{prefix_}/auth/signup'
    user_res = session_client.post(user_url, json=user)
    assert user_res.status_code==201
    user_data = schemas.GetUser(**user_res.json()).model_dump()
    user_data['password'] = user['password']
    ##
    # print(admin_data, user_data)
    return admin_data, user_data

@pytest.fixture()
def test_user_login(session_client, test_user_reg):
    '''
    Login and verify the newly created users and return their respective auth tokens.
    '''
    login_url = f'{prefix_}/auth/signin'
    admin, user = test_user_reg
    ##
    data = {
        'username': admin['email'],
        'password': admin['password']
    }
    # Login admin
    admin_login = session_client.post(login_url, data=data)
    assert admin_login.status_code==200
    admin_data = schemas.LoginRes(**admin_login.json()).model_dump()
    admin_access_token = admin_data['access_token']
    verified_admin = oauth2.verify_token(admin_access_token)
    assert data['username']==verified_admin.email 
    ##
    data = {
        'username': user['email'],
        'password': user['password']
    }
    # Login user
    user_login = session_client.post(login_url, data=data)
    assert user_login.status_code==200
    user_data = schemas.LoginRes(**user_login.json()).model_dump()
    user_access_token = user_data['access_token']
    verified_user = oauth2.verify_token(user_access_token)
    assert data['username']==verified_user.email 
    ##
    return admin_access_token, user_access_token

@pytest.fixture()
def authorized_admin(session_client, test_user_login):
    token, _ = test_user_login
    session_client.headers = {
        **session_client.headers,
        'Authorization': f'Bearer {token}'
    }
    return session_client

@pytest.fixture()
def authorized_user(session_client, test_user_login):
    _, token = test_user_login
    session_client.headers = {
        **session_client.headers,
        'Authorization': f'Bearer {token}'
    }
    return session_client

@pytest.fixture()
def test_create_event(authorized_admin):
    '''
    This tests for how an event event would be created by an admin.
    '''
    create_url = f'{prefix_}/events/'
    client = authorized_admin
    res = client.post(create_url, json=event)
    assert res.status_code==201
    res_data = schemas.CreatedEvent(**res.json()).model_dump()
    assert res_data['name']==event["name"]
