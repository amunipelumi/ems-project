##
from ems_api.api.v1 import schemas
from ems_api.__ import prefix_



update_event = {
    "name": "Update test event",
    "description": "This event is for testing purpose",
    "starts": "2024-10-30T14:00:00+01:00",
    "category": {
        "name": "Update"
    },
    "venue": {
        "name": "Update 55",
        "address": "Road 66",
        "city": "City 77",
        "country": "Country 88",
        "capacity": 99
    },
    "tickets": [
        {
            "type": "Regular",
            "price": 20.0,
            "quantity": 50,
        }
    ]
}

def test_update_event(authorized_admin, test_create_event):
    update_url = f'{prefix_}/events/1'
    client = authorized_admin
    res = client.put(update_url, json=update_event)
    assert res.status_code==202
    res_data = schemas.CreatedEvent(**res.json()).model_dump()
    assert res_data['name']==update_event['name']
    assert res_data['category']['name']==update_event['category']['name']

def test_delete_event(authorized_admin, test_create_event):
    delete_url = f'{prefix_}/events/1'
    client =authorized_admin
    res = client.delete(delete_url)
    assert res.status_code==204
