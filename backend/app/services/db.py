from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.invoice import ExtractedInvoice
from ..models.extraction import Extraction
from ..models.llm_config import LLMConfig
from ..schemas.llm_config import LLMConfigCreate


class DatabaseService:
    """Service for database operations using SQLAlchemy."""

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    def _build_record(
        self,
        extraction_id: str,
        filename: str,
        user_id: str,
        data: ExtractedInvoice,
        status: str,
    ) -> Dict[str, Any]:
        return {
            "id": extraction_id,
            "filename": filename,
            "user_id": user_id,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "vendor_name": data.vendor_name,
            "invoice_number": data.invoice_number,
            "invoice_date": data.invoice_date,
            "due_date": data.due_date,
            "subtotal": data.subtotal,
            "tax": data.tax,
            "total_amount": data.total_amount,
            "currency": data.currency,
            "entry_type": data.entry_type,
            "amount_paid": data.amount_paid,
            "full_data": data.model_dump() if hasattr(data, 'model_dump') else data.dict(),
        }

    async def save_extraction(
        self,
        extraction_id: str,
        filename: str,
        user_id: str,
        data: ExtractedInvoice,
        status: str
    ) -> Dict[str, Any]:
        """Save extraction to database."""
        if not self.db:
            raise RuntimeError("Database session not provided")

        record = self._build_record(extraction_id, filename, user_id, data, status)
        
        extraction = Extraction(
            id=extraction_id,
            user_id=user_id,
            filename=filename,
            status=status,
            vendor_name=data.vendor_name,
            invoice_number=data.invoice_number,
            invoice_date=data.invoice_date,
            due_date=data.due_date,
            subtotal=data.subtotal,
            tax=data.tax,
            total_amount=data.total_amount,
            currency=data.currency,
            entry_type=data.entry_type,
            amount_paid=data.amount_paid,
            full_data=data.model_dump() if hasattr(data, 'model_dump') else data.dict(),
        )
        
        self.db.add(extraction)
        await self.db.commit()
        await self.db.refresh(extraction)
        
        return {
            "id": str(extraction.id),
            "filename": extraction.filename,
            "user_id": str(extraction.user_id),
            "status": extraction.status,
            "created_at": extraction.created_at.isoformat() if extraction.created_at else "",
            "vendor_name": extraction.vendor_name,
            "invoice_number": extraction.invoice_number,
            "invoice_date": extraction.invoice_date,
            "due_date": extraction.due_date,
            "subtotal": extraction.subtotal,
            "tax": extraction.tax,
            "total_amount": extraction.total_amount,
            "currency": extraction.currency,
            "entry_type": extraction.entry_type,
            "amount_paid": extraction.amount_paid,
            "full_data": extraction.full_data,
        }

    async def get_extraction_by_id(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        if not self.db:
            raise RuntimeError("Database session not provided")

        result = await self.db.execute(
            select(Extraction).where(Extraction.id == extraction_id)
        )
        extraction = result.scalar_one_or_none()
        
        if not extraction:
            return None
            
        return {
            "id": str(extraction.id),
            "filename": extraction.filename,
            "user_id": str(extraction.user_id),
            "status": extraction.status,
            "created_at": extraction.created_at.isoformat() if extraction.created_at else "",
            "vendor_name": extraction.vendor_name,
            "invoice_number": extraction.invoice_number,
            "invoice_date": extraction.invoice_date,
            "due_date": extraction.due_date,
            "subtotal": extraction.subtotal,
            "tax": extraction.tax,
            "total_amount": extraction.total_amount,
            "currency": extraction.currency,
            "entry_type": extraction.entry_type,
            "amount_paid": extraction.amount_paid,
            "full_data": extraction.full_data,
        }

    async def update_extraction(self, extraction_id: str, data: ExtractedInvoice) -> Optional[Dict[str, Any]]:
        if not self.db:
            raise RuntimeError("Database session not provided")

        result = await self.db.execute(
            select(Extraction).where(Extraction.id == extraction_id)
        )
        extraction = result.scalar_one_or_none()
        
        if not extraction:
            return None

        extraction.vendor_name = data.vendor_name
        extraction.invoice_number = data.invoice_number
        extraction.invoice_date = data.invoice_date
        extraction.due_date = data.due_date
        extraction.subtotal = data.subtotal
        extraction.tax = data.tax
        extraction.total_amount = data.total_amount
        extraction.currency = data.currency
        extraction.entry_type = data.entry_type
        extraction.amount_paid = data.amount_paid
        extraction.full_data = data.model_dump() if hasattr(data, 'model_dump') else data.dict()
        extraction.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(extraction)
        
        return {
            "id": str(extraction.id),
            "filename": extraction.filename,
            "user_id": str(extraction.user_id),
            "status": extraction.status,
            "created_at": extraction.created_at.isoformat() if extraction.created_at else "",
            "vendor_name": extraction.vendor_name,
            "invoice_number": extraction.invoice_number,
            "invoice_date": extraction.invoice_date,
            "due_date": extraction.due_date,
            "subtotal": extraction.subtotal,
            "tax": extraction.tax,
            "total_amount": extraction.total_amount,
            "currency": extraction.currency,
            "entry_type": extraction.entry_type,
            "amount_paid": extraction.amount_paid,
            "full_data": extraction.full_data,
        }

    async def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        if not self.db:
            raise RuntimeError("Database session not provided")

        result = await self.db.execute(
            select(Extraction)
            .where(Extraction.user_id == user_id)
            .order_by(desc(Extraction.created_at))
        )
        extractions = result.scalars().all()
        
        return [
            {
                "id": str(e.id),
                "filename": e.filename,
                "user_id": str(e.user_id),
                "status": e.status,
                "created_at": e.created_at.isoformat() if e.created_at else "",
                "vendor_name": e.vendor_name,
                "invoice_number": e.invoice_number,
                "invoice_date": e.invoice_date,
                "due_date": e.due_date,
                "subtotal": e.subtotal,
                "tax": e.tax,
                "total_amount": e.total_amount,
                "currency": e.currency,
                "entry_type": e.entry_type,
                "amount_paid": e.amount_paid,
                "full_data": e.full_data,
            }
            for e in extractions
        ]

    async def save_llm_config(
        self,
        user_id: str,
        config: LLMConfigCreate
    ) -> Dict[str, Any]:
        if not self.db:
            raise RuntimeError("Database session not provided")

        result = await self.db.execute(
            select(LLMConfig).where(LLMConfig.user_id == user_id)
        )
        existing = result.scalar_one_or_none()

        if existing is not None:
            existing.provider = config.provider
            existing.api_key = config.api_key
            existing.model = config.model
            existing.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(existing)
            
            return {
                "id": str(existing.id),
                "user_id": str(existing.user_id),
                "provider": existing.provider,
                "api_key": existing.api_key,
                "model": existing.model,
                "created_at": existing.created_at.isoformat() if existing.created_at is not None else "",
                "updated_at": existing.updated_at.isoformat() if existing.updated_at is not None else "",
            }
        else:
            import uuid
            llm_config = LLMConfig(
                id=uuid.uuid4(),
                user_id=user_id,
                provider=config.provider,
                api_key=config.api_key,
                model=config.model,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(llm_config)
            await self.db.commit()
            await self.db.refresh(llm_config)
            
            return {
                "id": str(llm_config.id),
                "user_id": str(llm_config.user_id),
                "provider": llm_config.provider,
                "api_key": llm_config.api_key,
                "model": llm_config.model,
                "created_at": llm_config.created_at.isoformat() if llm_config.created_at is not None else "",
                "updated_at": llm_config.updated_at.isoformat() if llm_config.updated_at is not None else "",
            }

    async def get_llm_config(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not self.db:
            raise RuntimeError("Database session not provided")

        result = await self.db.execute(
            select(LLMConfig).where(LLMConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            return None
            
        return {
            "id": str(config.id),
            "user_id": str(config.user_id),
            "provider": config.provider,
            "api_key": config.api_key,
            "model": config.model,
            "created_at": config.created_at.isoformat() if config.created_at else "",
            "updated_at": config.updated_at.isoformat() if config.updated_at else "",
        }