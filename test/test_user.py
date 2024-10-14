##
from ems_api.__ import prefix_

##
import pytest


login_url = f'{prefix_}/auth/signin'

def test_user_login(session_client, test_user_reg):
    admin, user = test_user_reg
    ##
    data = {
        'username': admin.email,
        'password': admin.password
    }
    admin_login = session_client.post(login_url, data=data)
    assert admin_login.status_code==200
    ##
    data = {
        'username': user.email,
        'password': user.password
    }
    user_login = session_client.post(login_url, data=data)
    assert user_login.status_code==200
