import importlib
import uuid
from fastapi.testclient import TestClient
from pathlib import Path

def test_crud_workflow(db_session):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'gender': 'male',
        'avatar_url': None,
    }
    response = client.post('/api/customers/', json=payload)
    assert response.status_code == 201
    customer_id = response.json()['id']

    response = client.get(f'/api/customers/{customer_id}')
    assert response.status_code == 200
    assert response.json()['email'] == 'john@example.com'

    response = client.patch(f'/api/customers/{customer_id}', json={'full_name': 'Jane Doe'})
    assert response.status_code == 200
    assert response.json()['full_name'] == 'Jane Doe'

    response = client.delete(f'/api/customers/{customer_id}')
    assert response.status_code == 204

    response = client.get(f'/api/customers/{customer_id}')
    assert response.status_code == 404


def create_customer(client):
    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'John Avatar',
        'email': 'avatar@example.com',
        'phone': '1234567890',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = client.post('/api/customers/', json=payload)
    assert resp.status_code == 201
    return resp.json()['id']


def test_upload_avatar_success(db_session, tmp_path):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    customer_id = create_customer(client)

    file_path = tmp_path / 'avatar.png'
    file_path.write_bytes(b'\x89PNG\r\n\x1a\n')

    with file_path.open('rb') as f:
        resp = client.post(
            f'/api/customers/{customer_id}/avatar',
            files={'file': ('avatar.png', f, 'image/png')}
        )

    assert resp.status_code == 200
    assert resp.json()['avatar_url'] is not None
    stored = Path(resp.json()['avatar_url'].lstrip('/'))
    assert stored.exists()


def test_upload_avatar_invalid_file(db_session, tmp_path):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    customer_id = create_customer(client)

    invalid_path = tmp_path / 'avatar.txt'
    invalid_path.write_text('not an image')

    with invalid_path.open('rb') as f:
        resp = client.post(
            f'/api/customers/{customer_id}/avatar',
            files={'file': ('avatar.txt', f, 'text/plain')}
        )

    assert resp.status_code == 400


def test_get_customers_query_param(db_session):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)

    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Alice Query',
        'email': 'alice@example.com',
        'phone': '0000000000',
        'gender': 'female',
        'avatar_url': None,
    }
    resp = client.post('/api/customers/', json=payload)
    assert resp.status_code == 201

    resp = client.get('/api/customers/?query=Alice')
    assert resp.status_code == 200
    assert any(c['email'] == 'alice@example.com' for c in resp.json())

    alias_resp = client.get('/api/customers/?search=Alice')
    assert alias_resp.status_code == 200
    assert resp.json() == alias_resp.json()

