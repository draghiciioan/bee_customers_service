from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.customer_tag import CustomerTag
from app.schemas.tag import TagCreate, TagResponse
from app.services.tag_service import TagService

router = APIRouter()


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tag for a customer.
    """
    tag_service = TagService(db)
    return tag_service.create_tag(tag)


@router.get("/customer/{customer_id}", response_model=List[TagResponse])
def get_customer_tags(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all tags for a specific customer.
    """
    tag_service = TagService(db)
    return tag_service.get_tags_by_customer(customer_id)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: UUID,
    db: Session = Depends(get_db)
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
