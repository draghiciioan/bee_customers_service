import importlib
import uuid
from fastapi.testclient import TestClient

def test_crud_workflow(db_session):
    main_module = importlib.reload(__import__('main'))
    client = TestClient(main_module.app)
    payload = {
        'user_id': str(uuid.uuid4()),
        'business_id': str(uuid.uuid4()),
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'gender': 'male',
        'avatar_url': None,
    }
    response = client.post('/api/customers/', json=payload)
    assert response.status_code == 201
    customer_id = response.json()['id']

    response = client.get(f'/api/customers/{customer_id}')
    assert response.status_code == 200
    assert response.json()['email'] == 'john@example.com'

    response = client.put(f'/api/customers/{customer_id}', json={'full_name': 'Jane Doe'})
    assert response.status_code == 200
    assert response.json()['full_name'] == 'Jane Doe'

    response = client.delete(f'/api/customers/{customer_id}')
    assert response.status_code == 204

    response = client.get(f'/api/customers/{customer_id}')
    assert response.status_code == 404

