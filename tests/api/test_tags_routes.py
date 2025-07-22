import importlib
import uuid
from fastapi.testclient import TestClient


def test_create_and_get_tags(db_session):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)

    customer_payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = client.post('/api/customers/', json=customer_payload)
    assert resp.status_code == 201
    customer_id = resp.json()['id']

    tag_payload = {
        'customer_id': customer_id,
        'label': 'VIP',
        'color': 'red',
        'priority': 5,
        'created_by': str(uuid.uuid4()),
    }
    resp = client.post('/api/customers/tags/', json=tag_payload)
    assert resp.status_code == 201
    tag_id = resp.json()['id']
    assert resp.json()['color'] == 'red'
    assert resp.json()['priority'] == 5
    assert resp.json()['created_by'] == tag_payload['created_by']

    resp = client.get(f'/api/customers/tags/customer/{customer_id}')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == tag_id
    assert data[0]['color'] == 'red'
    assert data[0]['priority'] == 5
    assert data[0]['created_by'] == tag_payload['created_by']
