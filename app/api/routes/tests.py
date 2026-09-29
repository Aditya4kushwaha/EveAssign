from fastapi import APIRouter, Depends, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.test import DiagnosticTestCreate, DiagnosticTestResponse, DiagnosticTestUpdate
from app.services import test_service
from app.api.deps import get_current_user, get_current_admin_user

router = APIRouter()

@router.get("", response_model=List[DiagnosticTestResponse])
async def list_tests(db: AsyncSession = Depends(get_db)):
    return await test_service.get_all_tests(db)

@router.get("/{test_id}", response_model=DiagnosticTestResponse)
async def get_test(test_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await test_service.get_test(db, test_id)

@router.post("", response_model=DiagnosticTestResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_admin_user)])
async def create_test(test_in: DiagnosticTestCreate, db: AsyncSession = Depends(get_db)):
    return await test_service.create_test(db, test_in)

@router.patch("/{test_id}", response_model=DiagnosticTestResponse, dependencies=[Depends(get_current_admin_user)])
async def update_test(test_id: uuid.UUID, test_in: DiagnosticTestUpdate, db: AsyncSession = Depends(get_db)):
    return await test_service.update_test(db, test_id, test_in)

@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
async def delete_test(test_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await test_service.delete_test(db, test_id)
