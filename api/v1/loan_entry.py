from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from config.dependencies import get_current_user
from models.user import User
from schemas.base import ResponseModel
from services.loan import LoanEntriesService
from schemas.loan import LoanEntriesRead, LoanEntriesCreate, LoanEntriesUpdate
from config.db import get_session

router = APIRouter(prefix="/loan_entries", tags=["loan entries"])


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_loan_entries(
    id: UUID | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
):
    return await LoanEntriesService.get_loan_entries(
        session=session, id=id, limit=limit, offset=offset
    )


@router.get("/{id}", response_model=LoanEntriesRead, status_code=status.HTTP_200_OK)
async def get_loan_entry(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanEntriesService.get_loan_entry(id=id, session=session)


@router.post("/", response_model=LoanEntriesRead, status_code=status.HTTP_201_CREATED)
async def create_loan_entry(
    data: LoanEntriesCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanEntriesService.create_loan_entry(data=data, session=session)


@router.put("/{id}", response_model=LoanEntriesRead, status_code=status.HTTP_200_OK)
async def update_loan_entry(
    id: UUID,
    data: LoanEntriesUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanEntriesService.update_loan_entry(id=id, data=data, session=session)


@router.delete("/{id}", response_model={}, status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan_entries(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanEntriesService.delete_loan_entry(id=id, session=session)
