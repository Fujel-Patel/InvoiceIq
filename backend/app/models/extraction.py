from __future__ import annotations

import uuid
from sqlalchemy import Column, DateTime, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    vendor_name = Column(String(255), nullable=True)
    invoice_number = Column(String(255), nullable=True)
    invoice_date = Column(String(50), nullable=True)
    due_date = Column(String(50), nullable=True)
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    entry_type = Column(String(10), nullable=True)
    amount_paid = Column(Float, nullable=True)
    full_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="extractions")