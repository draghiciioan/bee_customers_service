import importlib
from fastapi.testclient import TestClient


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
