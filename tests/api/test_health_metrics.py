import importlib
import pytest


@pytest.mark.asyncio
async def test_health_and_metrics_endpoints(db_session, async_client):
    main_module = importlib.reload(__import__('main'))
    client = async_client

    health_resp = await client.get('/health')
    assert health_resp.status_code == 200
    assert health_resp.json() == {'status': 'healthy'}

    metrics_resp = await client.get('/metrics')
    assert metrics_resp.status_code == 200
    assert '# HELP' in metrics_resp.text
