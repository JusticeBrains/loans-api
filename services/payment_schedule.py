from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.payment_schedule import PaymentSchedule
from schemas.base import ResponseModel
from schemas.payment_schedule import PaymentScheduleCreate, PaymentScheduleUpdate


class PaymentScheduleService:
    @staticmethod
    async def create_schedule(data: PaymentScheduleCreate, session: AsyncSession):
        schedule = PaymentSchedule.model_validate(data)

        session.add(schedule)
        await session.commit()
        await session.refresh(schedule)

        return schedule

    @staticmethod
    async def get_schedule(id: UUID, session: AsyncSession):
        query = select(PaymentSchedule).where(PaymentSchedule.id == id)
        result = await session.exec(query)

        schedule = result.unique().one_or_none()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment schedule not found",
            )

        return schedule

    @staticmethod
    async def get_schedules(
        session: AsyncSession,
        loan_entry_id: UUID | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        query = (
            select(PaymentSchedule)
            .order_by(PaymentSchedule.month.desc())
            .limit(limit=limit)
            .offset(offset=offset)
        )
        if loan_entry_id:
            query = query.where(PaymentSchedule.loan_entry_id == loan_entry_id)

        result = await session.exec(query)

        schedules = result.unique().all()
        count = len(schedules)

        return ResponseModel(count=count, results=schedules)

    @staticmethod
    async def delete_schedule(id: UUID, session: AsyncSession):
        schedule = await PaymentScheduleService.get_schedule(id=id, session=session)

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment schedule not found",
            )

        schedule.is_deleted = True

        session.add(schedule)
        await session.commit()
        await session.refresh(schedule)

        return {}

    @staticmethod
    async def update_schedule(
        id: UUID, data: PaymentScheduleUpdate, session: AsyncSession
    ):
        schedule = await PaymentScheduleService.get_schedule(id=id, session=session)

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment schedule not found",
            )

        schedule.sqlmodel_update(data.model_dump(exclude_unset=True))
        session.add(schedule)

        await session.flush()
        # await session.commit()
        # await session.refresh(schedule)

        return schedule

    @staticmethod
    async def delete_schedule_based_on_loan_entry_id(
        loan_entry_id: UUID, session: AsyncSession
    ):
        query = select(PaymentSchedule).where(
            PaymentSchedule.loan_entry_id == loan_entry_id
        )
        result = await session.exec(query)

        schedules = result.unique().all()

        for schedule in schedules:
            schedule.is_deleted = True
            session.add(schedule)
        await session.commit()
        await session.refresh(schedule)

        return {}
