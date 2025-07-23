import importlib
from fastapi.testclient import TestClient


def test_health_and_metrics_endpoints(db_session):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)

    health_resp = client.get('/health')
    assert health_resp.status_code == 200
    assert health_resp.json() == {'status': 'healthy'}

    metrics_resp = client.get('/metrics')
    assert metrics_resp.status_code == 200
    assert '# HELP' in metrics_resp.text
