import importlib
import uuid
from fastapi.testclient import TestClient


def create_customer(client, headers):
    payload = {
        "user_id": str(uuid.uuid4()),
        "business_id": str(uuid.uuid4()),
        "full_name": "Rate User",
        "email": "rate@example.com",
        "phone": "0712345678",
        "gender": "male",
        "avatar_url": None,
    }
    resp = client.post("/api/customers/", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_patch_rate_limit(db_session, auth_headers, internal_headers):
    main_module = importlib.reload(__import__("main"))
    client = TestClient(main_module.app)

    customer_id = create_customer(client, internal_headers)

    for i in range(5):
        resp = client.patch(
            f"/api/customers/{customer_id}",
            json={"full_name": f"User {i}"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    resp = client.patch(
        f"/api/customers/{customer_id}",
        json={"full_name": "Blocked"},
        headers=auth_headers,
    )
    assert resp.status_code == 429
