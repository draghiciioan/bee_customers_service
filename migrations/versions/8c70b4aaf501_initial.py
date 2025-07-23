"""initial

Revision ID: 8c70b4aaf501
Revises: 
Create Date: 2025-07-23 09:43:21.983141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c70b4aaf501'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "customers",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20)),
        sa.Column(
            "gender",
            sa.Enum("male", "female", "other", name="gender_enum"),
        ),
        sa.Column("avatar_url", sa.String(length=255)),
        sa.Column("total_orders", sa.Integer(), server_default="0"),
        sa.Column("total_appointments", sa.Integer(), server_default="0"),
        sa.Column("last_order_date", sa.Date()),
        sa.Column("last_appointment_date", sa.Date()),
        sa.Column("lifetime_value", sa.Numeric(10, 2), server_default="0.00"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.UniqueConstraint("user_id", "business_id", name="uq_user_per_business"),
    )
    op.create_index(
        "ix_customer_business_id", "customers", ["business_id"], unique=False
    )
    op.create_index("ix_customer_user_id", "customers", ["user_id"], unique=False)
    op.create_index(
        "ix_customer_full_name", "customers", ["full_name"], unique=False
    )
    op.create_index("ix_customer_phone", "customers", ["phone"], unique=False)

    op.create_table(
        "customer_tags",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id"),
            nullable=False,
        ),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("color", sa.String(length=20)),
        sa.Column("priority", sa.Integer(), server_default="0"),
        sa.Column("created_by", sa.dialects.postgresql.UUID(as_uuid=True)),
    )

    op.create_table(
        "customer_notes",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id"),
            nullable=False,
        ),
        sa.Column("content", sa.String(length=500), nullable=False),
        sa.Column(
            "created_by", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "customer_history",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id"),
            nullable=False,
        ),
        sa.Column("first_order_date", sa.Date()),
        sa.Column("first_appointment_date", sa.Date()),
        sa.Column("returned_orders", sa.Integer(), server_default="0"),
        sa.Column("cancelled_appointments", sa.Integer(), server_default="0"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("customer_history")
    op.drop_table("customer_notes")
    op.drop_table("customer_tags")
    op.drop_index("ix_customer_phone", table_name="customers")
    op.drop_index("ix_customer_full_name", table_name="customers")
    op.drop_index("ix_customer_user_id", table_name="customers")
    op.drop_index("ix_customer_business_id", table_name="customers")
    op.drop_table("customers")
    sa.Enum(name="gender_enum").drop(op.get_bind(), checkfirst=False)
