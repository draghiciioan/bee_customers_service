from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class TagBase(BaseModel):
    label: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    priority: int = 0
    created_by: Optional[UUID] = None


class TagCreate(TagBase):
    customer_id: UUID


class TagResponse(TagBase):
    id: UUID
    customer_id: UUID

    class Config:
        orm_mode = True
        from_attributes = True

