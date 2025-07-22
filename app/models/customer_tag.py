from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.db.database import Base


class CustomerTag(Base):
    __tablename__ = "customer_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    label = Column(String(50), nullable=False)  # ex: "VIP", "Blacklisted"
    
    # Could be extended with:
    # color = Column(String(20), nullable=True)  # ex: "red", "#FF0000"
    # priority = Column(Integer, default=0)
    # created_by = Column(UUID(as_uuid=True), nullable=True)