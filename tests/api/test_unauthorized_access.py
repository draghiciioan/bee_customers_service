import importlib
from fastapi.testclient import TestClient


def test_requires_auth():
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    resp = client.get('/api/customers/')
    assert resp.status_code in (401, 403)
