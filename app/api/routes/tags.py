from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.schemas.tag import TagCreate, TagResponse, TagsCreate
from app.services.tag_service import TagService
from app.api.dependencies import User, require_admin, trace_id_dependency

router = APIRouter()
customer_router = APIRouter()


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    trace_id: str = Depends(trace_id_dependency),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Create a new tag for a customer.
    """
    tag_service = TagService(db)
    try:
        return await tag_service.create_tag(tag, trace_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/customer/{customer_id}", response_model=List[TagResponse])
async def get_customer_tags(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Get all tags for a specific customer.
    """
    tag_service = TagService(db)
    return await tag_service.get_tags_by_customer(customer_id)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Delete a tag.
    """
    tag_service = TagService(db)
    success = await tag_service.delete_tag(tag_id)
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
async def create_customer_tags(
    customer_id: UUID,
    payload: TagsCreate,
    trace_id: str = Depends(trace_id_dependency),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Create one or multiple tags for a customer."""
    tag_service = TagService(db)
    labels = [payload.label] if payload.label else (payload.labels or [])
    try:
        created_tags = await tag_service.create_tags(customer_id, labels, trace_id=trace_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return created_tags


@customer_router.delete(
    "/{customer_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer_tag(
    customer_id: UUID,
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Delete a tag from a specific customer."""
    tag_service = TagService(db)
    success = await tag_service.delete_tag(tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    return None
