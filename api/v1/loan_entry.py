from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from config.dependencies import get_current_user
from models.user import User
from schemas.base import ResponseModel
from services.loan import LoanEntriesService
from schemas.loan import LoanEntriesRead, LoanEntriesCreate, LoanEntriesUpdate
from config.db import get_session
from utils.text_options import InterestCalculationType, InterestTerm

router = APIRouter(prefix="/loan_entries", tags=["loan entries"])


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_loan_entries(
    id: UUID | None = None,
    code: str | None = None,
    employee_id: UUID | None = None,
    employee_code: str | None = None,
    employee_fullname: str | None = None,
    national_id: str | None = None,
    loan_id: UUID | None = None,
    loan_name: str | None = None,
    description: str | None = None,
    interest_term: InterestTerm | None = None,
    calculation_type: InterestCalculationType | None = None,
    # company_id: UUID | None = None,
    exclude: bool | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
):
    return await LoanEntriesService.get_loan_entries(
        session=session,
        id=id,
        code=code,
        employee_id=employee_id,
        employee_code=employee_code,
        employee_fullname=employee_fullname,
        national_id=national_id,
        loan_id=loan_id,
        loan_name=loan_name,
        description=description,
        interest_term=interest_term,
        calculation_type=calculation_type,
        exclude=exclude,
        limit=limit,
        offset=offset,
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
    return await LoanEntriesService.create_loan_entry(
        data=data, session=session, current_user=current_user
    )


@router.put("/{id}", response_model=LoanEntriesRead, status_code=status.HTTP_200_OK)
async def update_loan_entry(
    id: UUID,
    data: LoanEntriesUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanEntriesService.update_loan_entry(
        id=id, data=data, session=session, current_user=current_user
    )


@router.delete("/{id}", response_model={}, status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan_entries(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await LoanEntriesService.delete_loan_entry(id=id, session=session)
