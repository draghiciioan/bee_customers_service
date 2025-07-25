import uuid
import pytest
from app.services.note_service import NoteService
from app.services.customer_service import CustomerService
from app.schemas.note import NoteCreatePayload
from app.schemas.customer import CustomerCreate, Gender


async def create_customer(service: CustomerService) -> uuid.UUID:
    data = CustomerCreate(
        user_id=uuid.uuid4(),
        business_id=uuid.uuid4(),
        full_name="Note User",
        email="note@example.com",
        phone="0712345678",
        gender=Gender.MALE,
        avatar_url=None,
    )
    customer = await service.create_customer(data, "init")
    return customer.id


@pytest.mark.asyncio
async def test_note_creation_emits_event(db_session, monkeypatch):
    customer_service = CustomerService(db_session)
    customer_id = await create_customer(customer_service)

    note_service = NoteService(db_session)

    captured = []

    async def dummy_publish(event_name: str, payload: dict, trace_id: str):
        captured.append((event_name, payload, trace_id))

    monkeypatch.setattr("app.services.event_publisher.publish_event", dummy_publish)

    payload = NoteCreatePayload(content="hello", created_by=uuid.uuid4())
    note = await note_service.create_customer_note(customer_id, payload, "trace123")

    assert len(captured) == 1
    name, event_payload, trace_id = captured[0]
    assert name == "v1.customer.note_added"
    assert event_payload["customer_id"] == str(customer_id)
    assert event_payload["note_id"] == str(note.id)
    assert event_payload["trace_id"] == "trace123"
    assert trace_id == "trace123"


@pytest.mark.asyncio
async def test_logging_on_note_creation(db_session, monkeypatch):
    customer_service = CustomerService(db_session)
    customer_id = await create_customer(customer_service)

    note_service = NoteService(db_session)

    captured = []

    async def dummy_log(event: str, data: dict, trace_id: str):
        captured.append((event, data, trace_id))

    monkeypatch.setattr("app.services.log_service.send_log", dummy_log)
    monkeypatch.setattr("app.services.note_service.send_log", dummy_log)

    payload = NoteCreatePayload(content="hello", created_by=uuid.uuid4())
    note = await note_service.create_customer_note(customer_id, payload, "trace_log")

    assert len(captured) == 1
    event, data_payload, trace_id = captured[0]
    assert event == "v1.customer.note_added"
    assert data_payload["customer_id"] == str(customer_id)
    assert data_payload["note_id"] == str(note.id)
    assert trace_id == "trace_log"
