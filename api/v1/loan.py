from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from config.db import get_session
from config.dependencies import get_current_user
from models.user import User
from schemas.loan import LoanCreate, LoanRead, LoanUpdate
from services.loan import LoanService
from schemas.base import ResponseModel


router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_loans(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanService.get_loans(session=session)


@router.get("/{id}", response_model=LoanRead, status_code=status.HTTP_200_OK)
async def get_loan(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanService.get_loan(id=id, session=session)


@router.post("/", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
async def create_loan(
    data: LoanCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanService.create_loan(data=data, session=session)


@router.patch("/{id}", response_model=LoanRead, status_code=status.HTTP_200_OK)
async def update_loan(
    id: UUID,
    data: LoanUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanService.update_loan(id=id, data=data, session=session)


@router.delete("/{id}", response_model={}, status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanService.delete_loan(id=id, session=session)
