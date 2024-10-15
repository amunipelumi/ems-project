##
from ems_api.api.v1 import schemas
from ems_api.__ import prefix_



admin_user = {
    'name': 'Updated Admin User',
    'username': 'admin_updated',
    'email': 'updated.admin@email.com',
}

user = {
    'name': 'Updated User',
    'username': 'user_updated',
    'email': 'updated.user@email.com',
}

def test_update_admin(authorized_admin):
    update_url = f'{prefix_}/users/me'
    client = authorized_admin
    ##
    res = client.put(update_url, json=admin_user)
    assert res.status_code==202
    res_data = schemas.UserTable(**res.json()).model_dump()
    assert admin_user['username']==res_data['username']
    assert admin_user['email']==res_data['email']

def test_update_user(authorized_user):
    update_url = f'{prefix_}/users/me'
    client = authorized_user
    ##
    res = client.put(update_url, json=user)
    assert res.status_code==202
    res_data = schemas.UserTable(**res.json()).model_dump()
    assert user['username']==res_data['username']
    assert user['email']==res_data['email']

def test_delete_user(authorized_user):
    delete_url = f'{prefix_}/users/me'
    client = authorized_user
    ##
    res = client.delete(delete_url)
    assert res.status_code==204
