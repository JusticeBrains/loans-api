from uuid import UUID


from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi import APIRouter, Depends, status

from config.db import get_session
from schemas.base import ResponseModel
from schemas.payment import PaymentCreate, PaymentRead
from schemas.payment_schedule import PaymentScheduleCreate, PaymentScheduleRead
from services.payment import PaymentService
from services.payment_schedule import PaymentScheduleService

router = APIRouter(prefix="/payment", tags=["Payment"])


# @router.post("/", response_model=PaymentScheduleRead)
# async def create_payment_schedule(
#     data: PaymentScheduleCreate, session: AsyncSession = Depends(get_session)
# ):
#     return await PaymentScheduleService.create_schedule(data=data, session=session)


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_200_OK)
async def create_payment(
    data: PaymentCreate, session: AsyncSession = Depends(get_session)
):
    return await PaymentService.create_payment(data=data, session=session)


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_payments(
    session: AsyncSession = Depends(get_session), limit: int = 10, offset: int = 0
):
    return await PaymentService.get_payments(
        session=session, limit=limit, offset=offset
    )


@router.get("/schedules/{id}", response_model=PaymentScheduleRead)
async def get_payment_schedule(id: UUID, session: AsyncSession = Depends(get_session)):
    return await PaymentScheduleService.get_schedule(id=id, session=session)


@router.get("/schedules", response_model=ResponseModel)
async def get_payment_schedules(
    session: AsyncSession = Depends(get_session), limit: int = 10, offset: int = 0
):
    return await PaymentScheduleService.get_schedules(
        session=session, limit=limit, offset=offset
    )
