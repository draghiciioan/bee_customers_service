import importlib
import uuid
from pathlib import Path
import pytest


async def create_customer(client, headers):
    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'Avatar User',
        'email': 'avatar@example.com',
        'phone': '0712345678',
        'gender': 'male',
        'avatar_url': None,
    }
    resp = await client.post('/api/customers/', json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()['id']


@pytest.mark.asyncio
async def test_upload_avatar_success(db_session, tmp_path, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client
    customer_id = await create_customer(client, internal_headers)

    file_path = tmp_path / 'avatar.png'
    file_path.write_bytes(b'\x89PNG\r\n\x1a\n')

    with file_path.open('rb') as f:
        resp = await client.post(
            f'/api/customers/{customer_id}/avatar',
            files={'file': ('avatar.png', f, 'image/png')},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    assert resp.json()['avatar_url'] is not None
    stored = Path(resp.json()['avatar_url'].lstrip('/'))
    assert stored.exists()


@pytest.mark.asyncio
async def test_upload_avatar_invalid_file(db_session, tmp_path, auth_headers, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client
    customer_id = await create_customer(client, internal_headers)

    invalid_path = tmp_path / 'avatar.txt'
    invalid_path.write_text('not an image')

    with invalid_path.open('rb') as f:
        resp = await client.post(
            f'/api/customers/{customer_id}/avatar',
            files={'file': ('avatar.txt', f, 'text/plain')},
            headers=auth_headers,
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_avatar_requires_auth(db_session, tmp_path, internal_headers, async_client):
    importlib.reload(__import__('main'))
    client = async_client
    customer_id = await create_customer(client, internal_headers)

    file_path = tmp_path / 'avatar.png'
    file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
    with file_path.open('rb') as f:
        resp = await client.post(
            f'/api/customers/{customer_id}/avatar',
            files={'file': ('avatar.png', f, 'image/png')},
        )
    assert resp.status_code in (401, 403)
