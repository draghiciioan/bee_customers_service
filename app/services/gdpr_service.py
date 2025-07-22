from sqlalchemy.orm import Session
from typing import Dict, Optional, List
from uuid import UUID

from app.models.customer import Customer
from app.models.customer_tag import CustomerTag
from app.models.customer_note import CustomerNote
from app.models.customer_history import CustomerHistory


class GDPRService:
    def __init__(self, db: Session):
        self.db = db

    def export_customer_data(self, user_id: UUID, business_id: UUID) -> Optional[Dict]:
        """
        Export all data for a specific customer (GDPR compliance).
        """
        # Get customer
        customer = self.db.query(Customer).filter(
            Customer.user_id == user_id,
            Customer.business_id == business_id
        ).first()
        
        if not customer:
            return None
            
        # Get customer tags
        tags = self.db.query(CustomerTag).filter(
            CustomerTag.customer_id == customer.id
        ).all()
        
        # Get customer notes
        notes = self.db.query(CustomerNote).filter(
            CustomerNote.customer_id == customer.id
        ).all()
        
        # Get customer history
        history = self.db.query(CustomerHistory).filter(
            CustomerHistory.customer_id == customer.id
        ).first()
        
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

    def delete_customer_data(self, user_id: UUID, business_id: UUID) -> bool:
        """
        Delete all data for a specific customer (GDPR compliance).
        """
        # Get customer
        customer = self.db.query(Customer).filter(
            Customer.user_id == user_id,
            Customer.business_id == business_id
        ).first()
        
        if not customer:
            return False
            
        # Delete customer tags
        self.db.query(CustomerTag).filter(
            CustomerTag.customer_id == customer.id
        ).delete()
        
        # Delete customer notes
        self.db.query(CustomerNote).filter(
            CustomerNote.customer_id == customer.id
        ).delete()
        
        # Delete customer history
        self.db.query(CustomerHistory).filter(
            CustomerHistory.customer_id == customer.id
        ).delete()
        
        # Delete customer
        self.db.delete(customer)
        self.db.commit()
        
        return True