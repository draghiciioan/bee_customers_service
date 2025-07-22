from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.db.database import Base


class CustomerHistory(Base):
    __tablename__ = "customer_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)

    first_order_date = Column(Date)
    first_appointment_date = Column(Date)
    returned_orders = Column(Integer, default=0)
    cancelled_appointments = Column(Integer, default=0)