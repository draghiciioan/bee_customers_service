import importlib
import uuid
import pytest


@pytest.mark.asyncio
async def test_create_and_get_tags(db_session, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client

    customer_payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'phone': '0712345678',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=customer_payload, headers=internal_headers)
    assert resp.status_code == 201
    customer_id = resp.json()['id']

    tag_payload = {
        'customer_id': customer_id,
        'label': 'VIP',
        'color': 'red',
        'priority': 5,
        'created_by': str(uuid.uuid4()),
    }
    resp = await client.post('/api/customers/tags/', json=tag_payload, headers=auth_headers)
    assert resp.status_code == 201
    tag_id = resp.json()['id']
    assert resp.json()['color'] == 'red'
    assert resp.json()['priority'] == 5
    assert resp.json()['created_by'] == tag_payload['created_by']

    resp = await client.get(f'/api/customers/tags/customer/{customer_id}', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == tag_id
    assert data[0]['color'] == 'red'
    assert data[0]['priority'] == 5
    assert data[0]['created_by'] == tag_payload['created_by']


@pytest.mark.asyncio
async def test_create_and_delete_tags_new_routes(db_session, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client

    customer_payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Jane Doe',
        'email': 'jane@example.com',
        'phone': '0712345678',
        'gender': 'female',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=customer_payload, headers=internal_headers)
    assert resp.status_code == 201
    customer_id = resp.json()['id']

    resp = await client.post(
        f'/api/customers/{customer_id}/tags',
        json={'label': 'VIP'},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()[0]['label'] == 'VIP'
    tag_id = resp.json()[0]['id']

    resp = await client.post(
        f'/api/customers/{customer_id}/tags',
        json={'labels': ['Frequent', 'Loyal']},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert len(resp.json()) == 2

    resp = await client.delete(
        f'/api/customers/{customer_id}/tags/{tag_id}',
        headers=auth_headers,
    )
    assert resp.status_code == 204

    resp = await client.get(f'/api/customers/tags/customer/{customer_id}', headers=auth_headers)
    assert resp.status_code == 200
    labels = [t['label'] for t in resp.json()]
    assert 'VIP' not in labels


@pytest.mark.asyncio
async def test_duplicate_tags_returns_400(db_session, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client

    customer_payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Dup User',
        'email': 'dup@example.com',
        'phone': '0712345678',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=customer_payload, headers=internal_headers)
    assert resp.status_code == 201
    customer_id = resp.json()['id']

    resp = await client.post(
        f'/api/customers/{customer_id}/tags',
        json={'label': 'VIP'},
        headers=auth_headers,
    )
    assert resp.status_code == 201

    resp = await client.post(
        f'/api/customers/{customer_id}/tags',
        json={'label': 'VIP'},
        headers=auth_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_tag_wrong_customer_returns_404(db_session, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client

    # Create first customer and tag
    payload1 = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Owner',
        'email': 'owner@example.com',
        'phone': '0712345678',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=payload1, headers=internal_headers)
    assert resp.status_code == 201
    customer_id1 = resp.json()['id']

    resp = await client.post(
        f'/api/customers/{customer_id1}/tags',
        json={'label': 'VIP'},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    tag_id = resp.json()[0]['id']

    # Create another customer
    payload2 = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Other',
        'email': 'other@example.com',
        'phone': '0712345678',
        'gender': 'female',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=payload2, headers=internal_headers)
    assert resp.status_code == 201
    customer_id2 = resp.json()['id']

    # Attempt deletion with wrong customer_id
    resp = await client.delete(
        f'/api/customers/{customer_id2}/tags/{tag_id}',
        headers=auth_headers,
    )
    assert resp.status_code == 404

    # Verify tag still exists for original customer
    resp = await client.get(f'/api/customers/tags/customer/{customer_id1}', headers=auth_headers)
    assert resp.status_code == 200
    labels = [t['id'] for t in resp.json()]
    assert tag_id in labels
