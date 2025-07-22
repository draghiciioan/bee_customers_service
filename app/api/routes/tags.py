from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.schemas.tag import TagCreate, TagResponse, TagsCreate
from app.services.tag_service import TagService
from app.api.dependencies import User, require_admin
from app.core.tracing import get_trace_id
from fastapi import Request

router = APIRouter()
customer_router = APIRouter()


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag: TagCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Create a new tag for a customer.
    """
    tag_service = TagService(db)
    trace_id = get_trace_id(request)
    return tag_service.create_tag(tag, trace_id)


@router.get("/customer/{customer_id}", response_model=List[TagResponse])
def get_customer_tags(
    customer_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Get all tags for a specific customer.
    """
    tag_service = TagService(db)
    return tag_service.get_tags_by_customer(customer_id)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Delete a tag.
    """
    tag_service = TagService(db)
    success = tag_service.delete_tag(tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return None


@customer_router.post(
    "/{customer_id}/tags",
    response_model=List[TagResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_customer_tags(
    customer_id: UUID,
    payload: TagsCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Create one or multiple tags for a customer."""
    tag_service = TagService(db)
    labels = [payload.label] if payload.label else (payload.labels or [])
    trace_id = get_trace_id(request)
    created_tags = tag_service.create_tags(customer_id, labels, trace_id=trace_id)
    return created_tags


@customer_router.delete(
    "/{customer_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer_tag(
    customer_id: UUID,
    tag_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Delete a tag from a specific customer."""
    tag_service = TagService(db)
    success = tag_service.delete_tag(tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    return None
