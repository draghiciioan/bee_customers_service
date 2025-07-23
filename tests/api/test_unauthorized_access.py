import importlib
import uuid
import jwt
from fastapi.testclient import TestClient
from app.core.config import settings


def test_requires_auth():
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    resp = client.get('/api/customers/')
    assert resp.status_code in (401, 403)


def test_get_customer_requires_auth():
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    resp = client.get('/api/customers/00000000-0000-0000-0000-000000000000')
    assert resp.status_code in (401, 403)


def test_delete_customer_requires_auth():
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    resp = client.delete('/api/customers/00000000-0000-0000-0000-000000000000')
    assert resp.status_code in (401, 403)


def test_gdpr_export_requires_auth():
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    payload = {'user_id': "00000000-0000-0000-0000-000000000000", 'business_id': "00000000-0000-0000-0000-000000000000"}
    resp = client.post('/api/gdpr/export', json=payload)
    assert resp.status_code in (401, 403)


def test_gdpr_delete_requires_auth():
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    payload = {'user_id': "00000000-0000-0000-0000-000000000000", 'business_id': "00000000-0000-0000-0000-000000000000"}
    resp = client.post('/api/gdpr/delete', json=payload)
    assert resp.status_code in (401, 403)


def test_customer_detail_without_token():
    """Requesting a customer by ID without providing a JWT should be rejected."""
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    resp = client.get('/api/customers/11111111-1111-1111-1111-111111111111')
    assert resp.status_code in (401, 403)


def test_gdpr_export_forbidden_role():
    """GDPR export should require a customer or admin role."""
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
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
    resp = client.post('/api/gdpr/export', json=payload, headers=headers)
    assert resp.status_code == 403


def test_gdpr_delete_forbidden_role():
    """GDPR delete should require a customer or admin role."""
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
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
    resp = client.post('/api/gdpr/delete', json=payload, headers=headers)
    assert resp.status_code == 403
