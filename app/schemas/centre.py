from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List, Optional
from app.schemas.test import DiagnosticTestResponse

class DiagnosticCentreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)

class DiagnosticCentreCreate(DiagnosticCentreBase):
    pass

class DiagnosticCentreUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None

class DiagnosticCentreResponse(DiagnosticCentreBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DiagnosticCentreWithTestsResponse(DiagnosticCentreResponse):
    tests: List[DiagnosticTestResponse] = []
