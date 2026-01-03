from uuid import UUID
from datetime import date
from fastapi import HTTPException, status

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


from models.period_year import PeriodYear, Period
from models.user import User
from schemas.base import ResponseModel
from schemas.period_year import (
    PeriodCreate,
    PeriodRead,
    PeriodYearCreate,
)
from utils.helper import (
    MONTH_NAMES,
    count_working_days,
    generate_calender,
    get_days_in_month,
)


class PeriodYearService:
    @staticmethod
    async def create_period_year(
        data: PeriodYearCreate, session: AsyncSession, current_user: User
    ):
        try:
            period_year = PeriodYear.model_validate(
                data, update={"user_id": current_user.id}
            )

            session.add(period_year)
            await session.commit()
            await session.refresh(period_year)

            month_calender = generate_calender(period_year.year)
            for month, calender in month_calender.items():
                if calender:
                    first_day = calender[0][0]
                    last_week = calender[-1]
                    last_day = last_week[-1] if last_week[-1] != 0 else last_week[-2]
                    days_in_month = get_days_in_month(
                        year=period_year.year, month=month
                    )
                    period_code = f"{MONTH_NAMES.get(month)[:3].upper()}{str(period_year.year)[2:]}"
                    period_name = f"{MONTH_NAMES.get(month)} {period_year.year}"
                    start_date = date(period_year.year, month, first_day)
                    end_date = date(period_year.year, month, last_day)
                    no_of_days = days_in_month
                    total_working_days = count_working_days(
                        start_date=start_date, end_date=end_date
                    )
                    total_working_hours = total_working_days * 8
                    total_hours_per_day = 8
                    data = {
                        "period_year_id": period_year.id,
                        "month": month,
                        "month_calender": calender,
                        "year": period_year.year,
                        "user_id": current_user.id,
                        "period_code": period_code,
                        "period_name": period_name,
                        "start_date": start_date,
                        "end_date": end_date,
                        "no_of_days": no_of_days,
                        "total_working_days": total_working_days,
                        "total_working_hours": total_working_hours,
                        "total_hours_per_day": total_hours_per_day,
                    }
                    period_data = PeriodCreate(**data)
                    period = await PeriodService.create_period(
                        data=period_data, session=session
                    )
            return period_year
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def get_period(id: int, session: AsyncSession):
        query = select(PeriodYear).where(PeriodYear.id == id)
        result = await session.exec(query)

        period_year = result.unique().one_or_none()

        if not period_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, details="Period year not found"
            )

        return period_year

    @staticmethod
    async def get_periods(
        session: AsyncSession,
        year: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        try:
            query = (
                select(PeriodYear)
                .order_by(PeriodYear.year.desc())
                .limit(limit=limit)
                .offset(offset=offset)
            )

            if year:
                query = query.where(PeriodYear.year == year)

            results = await session.exec(query)
            periods = results.unique().all()

            count = len(periods)

            return ResponseModel(count=count, results=periods)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def delete_period(id: int, session: AsyncSession):
        try:
            period_year = await PeriodYearService.get_period(id=id, session=session)

            if not period_year:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    details="Period year not found",
                )

            await session.delete(period_year)
            await session.commit()

            return {}
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)[:100]
            )


class PeriodService:
    @staticmethod
    async def create_period(data: PeriodCreate, session: AsyncSession):
        try:
            period_year = await PeriodYearService.get_period(
                id=data.period_year_id, session=session
            )
            extra_fields = {"period_year": period_year}
            period = Period.model_validate(data, update=extra_fields)

            session.add(period)
            await session.commit()
            await session.refresh(period)

            return period
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)[:100]
            )

    @staticmethod
    async def get_periods(
        session: AsyncSession,
        period_code: str | None = None,
        period_name: str | None = None,
        period_year_id: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        try:
            query = (
                select(Period)
                .order_by(Period.period_code.desc())
                .limit(limit=limit)
                .offset(offset=offset)
            )

            if period_code:
                query = query.where(Period.period_code == period_code)
            if period_name:
                query = query.where(Period.period_name == period_name)
            if period_year_id:
                query = query.where(Period.period_year_id == period_year_id)

            results = await session.exec(query)
            periods = results.unique().all()

            count = len(periods)
            periods_result = [PeriodRead.model_validate(period) for period in periods]
            return ResponseModel(count=count, results=periods_result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def get_period(id: UUID, session: AsyncSession):
        try:
            query = select(Period).where(Period.id == id)
            result = await session.exec(query)

            period = result.unique().one_or_none()

            if not period:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, details="Period not found"
                )

            return period
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
