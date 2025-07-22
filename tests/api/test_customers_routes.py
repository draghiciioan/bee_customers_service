import importlib
import uuid
from fastapi.testclient import TestClient

def test_crud_workflow(db_session, auth_headers, internal_headers):
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
    response = client.post('/api/customers/', json=payload, headers=internal_headers)
    assert response.status_code == 201
    customer_id = response.json()['id']

    response = client.get(f'/api/customers/{customer_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['email'] == 'john@example.com'

    response = client.patch(
        f'/api/customers/{customer_id}',
        json={'full_name': 'Jane Doe'},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()['full_name'] == 'Jane Doe'

    response = client.delete(f'/api/customers/{customer_id}', headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f'/api/customers/{customer_id}', headers=auth_headers)
    assert response.status_code == 404


def test_get_customers_query_param(db_session, auth_headers, internal_headers):
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
    resp = client.post('/api/customers/', json=payload, headers=internal_headers)
    assert resp.status_code == 201

    resp = client.get('/api/customers/?query=Alice', headers=auth_headers)
    assert resp.status_code == 200
    assert any(c['email'] == 'alice@example.com' for c in resp.json())

    alias_resp = client.get('/api/customers/?search=Alice', headers=auth_headers)
    assert alias_resp.status_code == 200
    assert resp.json() == alias_resp.json()


def test_stats_endpoint(db_session, auth_headers, internal_headers):
    """Ensure the /stats endpoint returns customer statistics."""
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)

    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Stat Test',
        'email': 'stat@example.com',
        'phone': '1111111111',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = client.post('/api/customers/', json=payload, headers=internal_headers)
    assert resp.status_code == 201
    customer_id = resp.json()['id']

    stats_resp = client.get(f'/api/customers/{customer_id}/stats', headers=auth_headers)
    assert stats_resp.status_code == 200
    assert 'total_orders' in stats_resp.json()

