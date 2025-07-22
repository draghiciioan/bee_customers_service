import uuid
from app.services.tag_service import TagService
from app.services.customer_service import CustomerService
from app.schemas.tag import TagCreate
from app.schemas.customer import CustomerCreate, Gender


def create_sample_customer(service: CustomerService) -> uuid.UUID:
    data = CustomerCreate(
        user_id=uuid.uuid4(),
        business_id=uuid.uuid4(),
        full_name="John Doe",
        email="john@example.com",
        phone="1234567890",
        gender=Gender.MALE,
        avatar_url=None,
    )
    customer = service.create_customer(data, "test")
    return customer.id


def test_create_and_get_tag(db_session):
    customer_service = CustomerService(db_session)
    customer_id = create_sample_customer(customer_service)

    tag_service = TagService(db_session)
    tag_data = TagCreate(
        customer_id=customer_id,
        label="VIP",
        color="red",
        priority=1,
        created_by=uuid.uuid4(),
    )
    created = tag_service.create_tag(tag_data, "trace")

    retrieved = tag_service.get_tag(created.id)
    assert retrieved is not None
    assert retrieved.label == "VIP"
    assert retrieved.color == "red"
    assert retrieved.priority == 1
    assert retrieved.created_by == tag_data.created_by

    tags = tag_service.get_tags_by_customer(customer_id)
    assert len(tags) == 1
    assert tags[0].id == created.id


def test_create_multiple_tags(db_session):
    customer_service = CustomerService(db_session)
    customer_id = create_sample_customer(customer_service)

    tag_service = TagService(db_session)
    labels = ["VIP", "Regular"]
    created_tags = tag_service.create_tags(customer_id, labels, trace_id="trace")
    assert len(created_tags) == 2

    retrieved = tag_service.get_tags_by_customer(customer_id)
    assert sorted([t.label for t in retrieved]) == sorted(labels)


def test_tagging_emits_event(db_session, monkeypatch):
    customer_service = CustomerService(db_session)
    customer_id = create_sample_customer(customer_service)

    tag_service = TagService(db_session)

    captured = []

    async def dummy_publish(event_name: str, payload: dict, trace_id: str):
        captured.append((event_name, payload, trace_id))

    monkeypatch.setattr(
        "app.services.event_publisher.publish_event", dummy_publish
    )

    tag = tag_service.create_tag(
        TagCreate(customer_id=customer_id, label="VIP", created_by=uuid.uuid4()),
        "trace123",
    )

    assert len(captured) == 1
    name, payload, trace_id = captured[0]
    assert name == "v1.customer.tagged"
    assert payload["customer_id"] == str(customer_id)
    assert payload["tag_id"] == str(tag.id)
    assert payload["label"] == "VIP"
    assert payload["trace_id"] == "trace123"
    assert trace_id == "trace123"
