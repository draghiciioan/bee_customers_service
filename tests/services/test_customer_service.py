import uuid
import pytest
import httpx
from pydantic import ValidationError
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate, Gender


def create_sample_customer(service: CustomerService) -> uuid.UUID:
    data = CustomerCreate(
        user_id=uuid.uuid4(),
        business_id=uuid.uuid4(),
        full_name="John Doe",
        email="john@example.com",
        phone="0712345678",
        gender=Gender.MALE,
        avatar_url=None,
    )
    customer = service.create_customer(data, "test")
    return customer.id


def test_create_and_get_customer(db_session):
    service = CustomerService(db_session)
    customer_id = create_sample_customer(service)
    retrieved = service.get_customer(customer_id)
    assert retrieved is not None
    assert retrieved.full_name == "John Doe"


def test_update_customer(db_session):
    service = CustomerService(db_session)
    customer_id = create_sample_customer(service)
    update_data = CustomerUpdate(full_name="Jane Doe")
    updated = service.update_customer(customer_id, update_data, "trace")
    assert updated.full_name == "Jane Doe"


def test_delete_customer(db_session):
    service = CustomerService(db_session)
    customer_id = create_sample_customer(service)
    assert service.delete_customer(customer_id) is True
    assert service.get_customer(customer_id) is None


def test_create_customer_emits_event(db_session, monkeypatch):
    service = CustomerService(db_session)

    captured = []

    async def dummy_publish(event_name: str, payload: dict, trace_id: str):
        captured.append((event_name, payload, trace_id))

    monkeypatch.setattr("app.services.event_publisher.publish_event", dummy_publish)

    data = CustomerCreate(
        user_id=uuid.uuid4(),
        business_id=uuid.uuid4(),
        full_name="Event User",
        email="event@example.com",
        phone="0712345678",
        gender=Gender.MALE,
        avatar_url=None,
    )

    created = service.create_customer(data, "trace123")

    assert len(captured) == 1
    name, payload, trace_id = captured[0]
    assert name == "v1.customer.created"
    assert payload["id"] == str(created.id)
    assert payload["user_id"] == str(data.user_id)
    assert payload["business_id"] == str(data.business_id)
    assert payload["trace_id"] == "trace123"
    assert trace_id == "trace123"


def test_update_customer_emits_event(db_session, monkeypatch):
    service = CustomerService(db_session)

    data = CustomerCreate(
        user_id=uuid.uuid4(),
        business_id=uuid.uuid4(),
        full_name="Old Name",
        email="old@example.com",
        phone="0712345678",
        gender=Gender.MALE,
        avatar_url=None,
    )
    customer = service.create_customer(data, "init")

    captured = []

    async def dummy_publish(event_name: str, payload: dict, trace_id: str):
        captured.append((event_name, payload, trace_id))

    monkeypatch.setattr("app.services.event_publisher.publish_event", dummy_publish)

    update_data = CustomerUpdate(full_name="New Name")
    service.update_customer(customer.id, update_data, "trace_update")

    assert len(captured) == 1
    name, payload, trace_id = captured[0]
    assert name == "v1.customer.updated"
    assert payload["id"] == str(customer.id)
    assert "full_name" in payload["fields_changed"]
    assert payload["trace_id"] == "trace_update"
    assert trace_id == "trace_update"


def test_create_customer_invalid_phone():
    with pytest.raises(ValidationError):
        CustomerCreate(
            user_id=uuid.uuid4(),
            business_id=uuid.uuid4(),
            full_name="Bad",
            email="bad@example.com",
            phone="123",  # invalid
        )


def test_update_customer_invalid_phone():
    with pytest.raises(ValidationError):
        CustomerUpdate(phone="abc")


def test_logging_on_create(db_session, monkeypatch):
    service = CustomerService(db_session)

    captured = []

    async def dummy_log(event: str, data: dict, trace_id: str):
        captured.append((event, data, trace_id))

    monkeypatch.setattr("app.services.log_service.send_log", dummy_log)

    data = CustomerCreate(
        user_id=uuid.uuid4(),
        business_id=uuid.uuid4(),
        full_name="Log User",
        email="log@example.com",
        phone="0712345678",
        gender=Gender.MALE,
        avatar_url=None,
    )

    created = service.create_customer(data, "trace_log")

    assert len(captured) == 1
    event, payload, trace_id = captured[0]
    assert event == "v1.customer.created"
    assert payload["customer_id"] == str(created.id)
    assert payload["business_id"] == str(data.business_id)
    assert trace_id == "trace_log"


def test_auth_service_called_on_email_change(db_session, monkeypatch):
    service = CustomerService(db_session)
    customer_id = create_sample_customer(service)
    user_id = service.get_customer(customer_id).user_id

    called = []

    def dummy_patch(url, json, timeout):
        called.append((url, json))
        class Response:
            status_code = 200
        return Response()

    monkeypatch.setattr(httpx, "patch", dummy_patch)

    service.update_customer(customer_id, CustomerUpdate(email="new@example.com"), "trace")

    assert len(called) == 1
    url, data = called[0]
    assert url.endswith(f"/api/users/{user_id}")
    assert data == {"email": "new@example.com"}


def test_auth_service_called_on_phone_change(db_session, monkeypatch):
    service = CustomerService(db_session)
    customer_id = create_sample_customer(service)
    user_id = service.get_customer(customer_id).user_id

    called = []

    def dummy_patch(url, json, timeout):
        called.append((url, json))
        class Response:
            status_code = 200
        return Response()

    monkeypatch.setattr(httpx, "patch", dummy_patch)

    service.update_customer(customer_id, CustomerUpdate(phone="0799999999"), "trace")

    assert len(called) == 1
    url, data = called[0]
    assert url.endswith(f"/api/users/{user_id}")
    assert data == {"phone": "0799999999"}
