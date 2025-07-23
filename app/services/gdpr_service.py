from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Dict, Optional
from uuid import UUID

from app.models.customer import Customer
from app.models.customer_tag import CustomerTag
from app.models.customer_note import CustomerNote
from app.models.customer_history import CustomerHistory


class GDPRService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_customer_data(
        self, user_id: UUID, business_id: UUID
    ) -> Optional[Dict]:
        """
        Export all data for a specific customer (GDPR compliance).
        """
        # Get customer
        result = await self.db.execute(
            select(Customer).where(
                Customer.user_id == user_id,
                Customer.business_id == business_id,
            )
        )
        customer = result.scalars().first()
        
        if not customer:
            return None
            
        # Get customer tags using TagService for consistency
        from app.services.tag_service import TagService

        tag_service = TagService(self.db)
        tags = await tag_service.get_tags_by_customer(customer.id)
        
        # Get customer notes
        result = await self.db.execute(
            select(CustomerNote).where(CustomerNote.customer_id == customer.id)
        )
        notes = result.scalars().all()
        
        # Get customer history
        result = await self.db.execute(
            select(CustomerHistory).where(
                CustomerHistory.customer_id == customer.id
            )
        )
        history = result.scalars().first()
        
        # Prepare export data
        export_data = {
            "customer": {
                "id": str(customer.id),
                "user_id": str(customer.user_id),
                "business_id": str(customer.business_id),
                "full_name": customer.full_name,
                "email": customer.email,
                "phone": customer.phone,
                "gender": customer.gender,
                "avatar_url": customer.avatar_url,
                "total_orders": customer.total_orders,
                "total_appointments": customer.total_appointments,
                "last_order_date": customer.last_order_date.isoformat() if customer.last_order_date else None,
                "last_appointment_date": customer.last_appointment_date.isoformat() if customer.last_appointment_date else None,
                "lifetime_value": float(customer.lifetime_value) if customer.lifetime_value else 0.0,
                "created_at": customer.created_at.isoformat(),
                "updated_at": customer.updated_at.isoformat()
            },
            "tags": [
                {
                    "id": str(tag.id),
                    "label": tag.label
                }
                for tag in tags
            ],
            "notes": [
                {
                    "id": str(note.id),
                    "content": note.content,
                    "created_by": str(note.created_by),
                    "created_at": note.created_at.isoformat()
                }
                for note in notes
            ]
        }
        
        # Add history if exists
        if history:
            export_data["history"] = {
                "id": str(history.id),
                "first_order_date": history.first_order_date.isoformat() if history.first_order_date else None,
                "first_appointment_date": history.first_appointment_date.isoformat() if history.first_appointment_date else None,
                "returned_orders": history.returned_orders,
                "cancelled_appointments": history.cancelled_appointments
            }
            
        return export_data

    async def delete_customer_data(self, user_id: UUID, business_id: UUID) -> bool:
        """
        Delete all data for a specific customer (GDPR compliance).
        """
        # Get customer
        result = await self.db.execute(
            select(Customer).where(
                Customer.user_id == user_id,
                Customer.business_id == business_id,
            )
        )
        customer = result.scalars().first()
        
        if not customer:
            return False
            
        # Delete customer tags
        await self.db.execute(
            delete(CustomerTag).where(CustomerTag.customer_id == customer.id)
        )
        
        # Delete customer notes
        await self.db.execute(
            delete(CustomerNote).where(CustomerNote.customer_id == customer.id)
        )
        
        # Delete customer history
        await self.db.execute(
            delete(CustomerHistory).where(CustomerHistory.customer_id == customer.id)
        )
        
        # Delete customer
        await self.db.delete(customer)
        await self.db.commit()
        
        return True
