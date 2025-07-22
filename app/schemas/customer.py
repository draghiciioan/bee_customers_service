from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[constr(pattern=r"^(\+4|0)?7\d{8}$")] = Field(
        None, max_length=20
    )
    gender: Optional[Gender] = None
    avatar_url: Optional[str] = None


class CustomerCreate(CustomerBase):
    user_id: UUID
    business_id: UUID


class CustomerUpdate(CustomerBase):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[constr(pattern=r"^(\+4|0)?7\d{8}$")] = Field(
        None, max_length=20
    )


class CustomerResponse(CustomerBase):
    id: UUID
    user_id: UUID
    business_id: UUID
    total_orders: int = 0
    total_appointments: int = 0
    last_order_date: Optional[date] = None
    last_appointment_date: Optional[date] = None
    lifetime_value: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class CustomerStatistics(BaseModel):
    total_orders: int = 0
    total_appointments: int = 0
    last_order_date: Optional[date] = None
    last_appointment_date: Optional[date] = None
    lifetime_value: float = 0.0
