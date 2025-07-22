import uuid
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate, Gender


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

