from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List, Optional

class DiagnosticTestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

class DiagnosticTestCreate(DiagnosticTestBase):
    pass

class DiagnosticTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class DiagnosticTestResponse(DiagnosticTestBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
