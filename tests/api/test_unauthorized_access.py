import importlib
import uuid
import jwt
import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_requires_auth(async_client):
    importlib.reload(__import__('main'))
    resp = await async_client.get('/api/customers/')
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_customer_requires_auth(async_client):
    importlib.reload(__import__('main'))
    resp = await async_client.get('/api/customers/00000000-0000-0000-0000-000000000000')
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_delete_customer_requires_auth(async_client):
    importlib.reload(__import__('main'))
    resp = await async_client.delete('/api/customers/00000000-0000-0000-0000-000000000000')
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_gdpr_export_requires_auth(async_client):
    importlib.reload(__import__('main'))
    payload = {'user_id': "00000000-0000-0000-0000-000000000000", 'business_id': "00000000-0000-0000-0000-000000000000"}
    resp = await async_client.post('/api/gdpr/export', json=payload)
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_gdpr_delete_requires_auth(async_client):
    importlib.reload(__import__('main'))
    payload = {'user_id': "00000000-0000-0000-0000-000000000000", 'business_id': "00000000-0000-0000-0000-000000000000"}
    resp = await async_client.post('/api/gdpr/delete', json=payload)
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_customer_detail_without_token(async_client):
    """Requesting a customer by ID without providing a JWT should be rejected."""
    importlib.reload(__import__('main'))
    resp = await async_client.get('/api/customers/11111111-1111-1111-1111-111111111111')
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_gdpr_export_forbidden_role(async_client):
    """GDPR export should require a customer or admin role."""
    importlib.reload(__import__('main'))
    client = async_client
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "internal"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        'user_id': "00000000-0000-0000-0000-000000000000",
        'business_id': "00000000-0000-0000-0000-000000000000",
    }
    resp = await client.post('/api/gdpr/export', json=payload, headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_gdpr_delete_forbidden_role(async_client):
    """GDPR delete should require a customer or admin role."""
    importlib.reload(__import__('main'))
    client = async_client
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "internal"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        'user_id': "00000000-0000-0000-0000-000000000000",
        'business_id': "00000000-0000-0000-0000-000000000000",
    }
    resp = await client.post('/api/gdpr/delete', json=payload, headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_tags_routes_require_admin(async_client):
    """Creating or retrieving tags should require admin credentials."""
    importlib.reload(__import__('main'))
    # create tag without auth
    tag_payload = {"customer_id": str(uuid.uuid4()), "label": "VIP"}
    resp = await async_client.post('/api/customers/tags/', json=tag_payload)
    assert resp.status_code in (401, 403)

    # list tags without auth
    resp = await async_client.get('/api/customers/tags/customer/00000000-0000-0000-0000-000000000000')
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_notes_routes_require_admin(async_client):
    """Adding notes should require admin credentials."""
    importlib.reload(__import__('main'))
    note_payload = {"content": "test", "created_by": str(uuid.uuid4())}
    url = '/api/customers/00000000-0000-0000-0000-000000000000/notes'
    resp = await async_client.post(url, json=note_payload)
    assert resp.status_code in (401, 403)
