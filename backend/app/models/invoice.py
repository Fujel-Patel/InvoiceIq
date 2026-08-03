from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None

class ExtractedInvoice(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    line_items: List[LineItem] = []
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    entry_type: Optional[str] = None
    amount_paid: Optional[float] = None

class ExtractionResponse(BaseModel):
    extraction_id: str
    status: str
    data: ExtractedInvoice
    raw_text: Optional[str] = None

class HistoryItem(BaseModel):
    extraction_id: str
    filename: str
    extracted_at: str
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    amount_paid: Optional[float] = None
    balance_due: Optional[float] = None
    status: str

class ExportRequest(BaseModel):
    extraction_ids: List[str]
    format: str

# Rebuild models if necessary to resolve forward references
ExtractedInvoice.model_rebuild()
ExtractionResponse.model_rebuild()


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    GROQ = "groq"


class LLMConfigBase(BaseModel):
    provider: LLMProvider
    api_key: str
    model: str


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigUpdate(BaseModel):
    provider: Optional[LLMProvider] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


class LLMConfigResponse(BaseModel):
    provider: LLMProvider
    model: str
    is_valid: bool
    masked_api_key: str
    user_id: str


class VerifyLLMRequest(BaseModel):
    provider: LLMProvider
    api_key: str
    model: str


class VerifyLLMResponse(BaseModel):
    is_valid: bool
    message: str
    provider: LLMProvider


class LLMConfigInDBBase(LLMConfigBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LLMConfig(LLMConfigInDBBase):
    pass
