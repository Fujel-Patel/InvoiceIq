from __future__ import annotations

import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from .base import Base


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    vendor_name = Column(String(255), nullable=True)
    invoice_date = Column(String(50), nullable=True)
    total_amount = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    full_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())