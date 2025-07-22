from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from app.db.database import Base


class CustomerNote(Base):
    __tablename__ = "customer_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    content = Column(String(500), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)  # admin user_id
    created_at = Column(DateTime, default=datetime.utcnow)
