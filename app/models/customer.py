from sqlalchemy import Column, String, Integer, Date, DateTime, Numeric, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Conexiuni
    user_id = Column(UUID(as_uuid=True), unique=False, nullable=False)       # referință către user global
    business_id = Column(UUID(as_uuid=True), nullable=False)                 # profil local per afacere

    # Informații personale
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    gender = Column(Enum("male", "female", "other", name="gender_enum"))
    avatar_url = Column(String(255), nullable=True)  # link imagine avatar

    # Statistici agregate
    total_orders = Column(Integer, default=0)
    total_appointments = Column(Integer, default=0)
    last_order_date = Column(Date)
    last_appointment_date = Column(Date)
    lifetime_value = Column(Numeric(10, 2), default=0.00)

    # Timp
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "business_id", name="uq_user_per_business"),
    )