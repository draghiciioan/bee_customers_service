import uuid
import pytest
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

    monkeypatch.setattr(
        "app.services.event_publisher.publish_event", dummy_publish
    )

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

    monkeypatch.setattr(
        "app.services.event_publisher.publish_event", dummy_publish
    )

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

