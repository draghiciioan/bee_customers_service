import importlib
import uuid
import pytest


async def create_customer(client, headers):
    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Note User',
        'email': 'note@example.com',
        'phone': '0712345678',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()['id']


@pytest.mark.asyncio
async def test_note_routes(db_session, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client

    customer_id = await create_customer(client, internal_headers)
    payload = {
        'content': 'First note',
        'created_by': str(uuid.uuid4()),
    }

    resp = await client.post(
        f'/api/customers/{customer_id}/notes',
        json=payload,
        headers=auth_headers,
    )
    assert resp.status_code == 201
    note_id = resp.json()['id']
    assert resp.json()['content'] == 'First note'

    resp = await client.get(f'/api/customers/{customer_id}/notes', headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]['id'] == note_id

    resp = await client.delete(
        f'/api/customers/{customer_id}/notes/{note_id}',
        headers=auth_headers,
    )
    assert resp.status_code == 204

    resp = await client.get(f'/api/customers/{customer_id}/notes', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_note_routes_async(db_session, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Async User',
        'email': 'async@example.com',
        'phone': '0712345678',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = await async_client.post('/api/customers/', json=payload, headers=internal_headers)
    assert resp.status_code == 201
    customer_id = resp.json()['id']

    payload = {
        'content': 'Async note',
        'created_by': str(uuid.uuid4()),
    }
    resp = await async_client.post(f'/api/customers/{customer_id}/notes', json=payload, headers=auth_headers)
    assert resp.status_code == 201
    note_id = resp.json()['id']

    resp = await async_client.get(f'/api/customers/{customer_id}/notes', headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await async_client.delete(f'/api/customers/{customer_id}/notes/{note_id}', headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_notes_require_admin(db_session, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client
    customer_id = await create_customer(client, internal_headers)
    payload = {
        'content': 'No admin',
        'created_by': str(uuid.uuid4()),
    }
    resp = await client.post(f'/api/customers/{customer_id}/notes', json=payload, headers=internal_headers)
    assert resp.status_code == 403
