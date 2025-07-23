import importlib
from fastapi.testclient import TestClient


def test_metrics_endpoint(db_session):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    resp = client.get('/metrics')
    assert resp.status_code == 200
    assert '# HELP' in resp.text
    assert '# TYPE' in resp.text
