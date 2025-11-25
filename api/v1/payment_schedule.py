from uuid import UUID


from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi import APIRouter, Depends, status

from config.db import get_session
from config.dependencies import get_current_user
from models.user import User
from schemas.base import ResponseModel
from schemas.payment import PaymentCreate, PaymentRead
from schemas.payment_schedule import PaymentScheduleRead
from services.payment import PaymentService
from services.payment_schedule import PaymentScheduleService

router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_200_OK)
async def create_payment(
    data: PaymentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await PaymentService.create_payment(
        data=data, session=session, current_user=current_user
    )


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_payments(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
):
    return await PaymentService.get_payments(
        session=session, limit=limit, offset=offset
    )


@router.get("/schedules/{id}", response_model=PaymentScheduleRead)
async def get_payment_schedule(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await PaymentScheduleService.get_schedule(id=id, session=session)


@router.get("/schedules", response_model=ResponseModel)
async def get_payment_schedules(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    loan_entry_id: UUID = None,
    limit: int = 10,
    offset: int = 0,
):
    return await PaymentScheduleService.get_schedules(
        session=session, limit=limit, offset=offset, loan_entry_id=loan_entry_id
    )
