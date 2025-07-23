import importlib
import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint(db_session, async_client):
    main_module = importlib.reload(__import__('main'))
    client = async_client
    resp = await client.get('/metrics')
    assert resp.status_code == 200
    assert '# HELP' in resp.text
    assert '# TYPE' in resp.text
