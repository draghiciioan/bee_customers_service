import importlib
import uuid
import pytest

@pytest.mark.asyncio
async def test_crud_workflow(db_session, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client
    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'phone': '0712345678',
        'gender': 'male',
        'avatar_url': None,
    }
    response = await client.post('/api/customers/', json=payload, headers=internal_headers)
    assert response.status_code == 201
    customer_id = response.json()['id']

    response = await client.get(f'/api/customers/{customer_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['email'] == 'john@example.com'

    response = await client.patch(
        f'/api/customers/{customer_id}',
        json={'full_name': 'Jane Doe'},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()['full_name'] == 'Jane Doe'

    response = await client.delete(f'/api/customers/{customer_id}', headers=auth_headers)
    assert response.status_code == 204

    response = await client.get(f'/api/customers/{customer_id}', headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_customers_query_param(db_session, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client

    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Alice Query',
        'email': 'alice@example.com',
        'phone': '0712345678',
        'gender': 'female',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=payload, headers=internal_headers)
    assert resp.status_code == 201

    resp = await client.get('/api/customers/?query=Alice', headers=auth_headers)
    assert resp.status_code == 200
    assert any(c['email'] == 'alice@example.com' for c in resp.json())

    alias_resp = await client.get('/api/customers/?search=Alice', headers=auth_headers)
    assert alias_resp.status_code == 200
    assert resp.json() == alias_resp.json()


@pytest.mark.asyncio
async def test_stats_endpoint(db_session, auth_headers, internal_headers, async_client):
    """Ensure the /stats endpoint returns customer statistics."""
    importlib.reload(__import__('main'))
    client = async_client

    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Stat Test',
        'email': 'stat@example.com',
        'phone': '0712345678',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=payload, headers=internal_headers)
    assert resp.status_code == 201
    customer_id = resp.json()['id']

    stats_resp = await client.get(f'/api/customers/{customer_id}/stats', headers=auth_headers)
    assert stats_resp.status_code == 200
    assert 'total_orders' in stats_resp.json()

