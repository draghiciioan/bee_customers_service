from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
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


class TagsCreate(BaseModel):
    label: Optional[str] = None
    labels: Optional[List[str]] = None

    @field_validator('labels', mode='before')
    def validate_labels(cls, v):
        if v is None:
            return v
        if not isinstance(v, list) or not all(isinstance(i, str) for i in v):
            raise ValueError('labels must be a list of strings')
        return v

    @field_validator('label', mode='before')
    def validate_label(cls, v):
        if v is None:
            return v
        if not isinstance(v, str) or not v:
            raise ValueError('label must be a non-empty string')
        return v

    @model_validator(mode='after')
    def check_either(cls, data):
        if (data.label and data.labels) or (not data.label and not data.labels):
            raise ValueError('Provide either label or labels')
        return data


