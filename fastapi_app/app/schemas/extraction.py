from __future__ import annotations

from typing import Optional
from pydantic import BaseModel

from ..models.invoice import ExtractedInvoice


class ExtractionResponse(BaseModel):
    extraction_id: str
    status: str
    data: ExtractedInvoice
    raw_text: Optional[str] = None
