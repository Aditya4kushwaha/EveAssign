from fastapi import APIRouter, Depends, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.centre import DiagnosticCentreCreate, DiagnosticCentreResponse, DiagnosticCentreUpdate, DiagnosticCentreWithTestsResponse
from app.services import centre_service
from app.api.deps import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[DiagnosticCentreResponse])
async def list_centres(db: AsyncSession = Depends(get_db)):
    return await centre_service.get_all_centres(db)

@router.get("/{centre_id}", response_model=DiagnosticCentreWithTestsResponse)
async def get_centre(centre_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await centre_service.get_centre(db, centre_id)

@router.post("", response_model=DiagnosticCentreResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_admin_user)])
async def create_centre(centre_in: DiagnosticCentreCreate, db: AsyncSession = Depends(get_db)):
    return await centre_service.create_centre(db, centre_in)

@router.patch("/{centre_id}", response_model=DiagnosticCentreResponse, dependencies=[Depends(get_current_admin_user)])
async def update_centre(centre_id: uuid.UUID, centre_in: DiagnosticCentreUpdate, db: AsyncSession = Depends(get_db)):
    return await centre_service.update_centre(db, centre_id, centre_in)

@router.delete("/{centre_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
async def delete_centre(centre_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await centre_service.delete_centre(db, centre_id)

@router.post("/{centre_id}/tests/{test_id}", response_model=DiagnosticCentreWithTestsResponse, dependencies=[Depends(get_current_admin_user)])
async def add_test_to_centre(centre_id: uuid.UUID, test_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await centre_service.add_test_to_centre(db, centre_id, test_id)
