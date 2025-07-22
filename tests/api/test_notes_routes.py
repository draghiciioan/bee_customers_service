import importlib
import uuid
from fastapi.testclient import TestClient


def create_customer(client, headers):
    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Note User',
        'email': 'note@example.com',
        'phone': '5550000',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = client.post('/api/customers/', json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()['id']


def test_note_routes(db_session, auth_headers, internal_headers):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)

    customer_id = create_customer(client, internal_headers)
    payload = {
        'content': 'First note',
        'created_by': str(uuid.uuid4()),
    }

    resp = client.post(
        f'/api/customers/{customer_id}/notes',
        json=payload,
        headers=auth_headers,
    )
    assert resp.status_code == 201
    note_id = resp.json()['id']
    assert resp.json()['content'] == 'First note'

    resp = client.get(f'/api/customers/{customer_id}/notes', headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]['id'] == note_id

    resp = client.delete(
        f'/api/customers/{customer_id}/notes/{note_id}',
        headers=auth_headers,
    )
    assert resp.status_code == 204

    resp = client.get(f'/api/customers/{customer_id}/notes', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []
