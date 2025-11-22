from datetime import date, timedelta
import math
from pickle import TRUE
from unittest import result
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from dateutil.relativedelta import relativedelta

from models.loan import Loan, LoanEntries
from schemas.base import ResponseModel
from schemas.loan import LoanCreate, LoanEntriesCreate, LoanEntriesUpdate, LoanUpdate
from services.employee import EmployeeService
from services.payment_schedule import PaymentScheduleService
from services.period_year import PeriodService
from utils.helper import defualt_schedule_generation, delete_payment_by_loan_entry_id


class LoanService:

    @staticmethod
    async def create_loan(data: LoanCreate, session: AsyncSession):
        loan = Loan.model_validate(data)

        session.add(loan)
        await session.commit()
        await session.refresh(loan)

        return loan

    @staticmethod
    async def get_loan(id: UUID, session: AsyncSession):
        query = select(Loan).where(Loan.id == id)
        result = await session.exec(query)

        loan = result.unique().one_or_none()

        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found"
            )

        return loan

    @staticmethod
    async def get_loans(session: AsyncSession, limit: int = 10, offset: int = 0):
        query = (
            select(Loan).order_by(Loan.name).limit(limit=limit).offset(offset=offset)
        )
        result = await session.exec(query)

        loans = result.unique().all()
        count = len(loans)

        return ResponseModel(count=count, results=loans)

    @staticmethod
    async def delete_loan(id: UUID, session: AsyncSession):
        loan = await LoanService.get_loan(id=id, session=session)
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found"
            )
        setattr(loan, "exclude", True)
        session.add(loan)
        await session.commit()

        return {}

    @staticmethod
    async def update_loan(id: UUID, data: LoanUpdate, session: AsyncSession):
        loan = await LoanService.get_loan(id=id, session=session)
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found"
            )
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(loan, key, value)

        session.add(loan)
        await session.commit()
        await session.refresh(loan)

        return loan


class LoanEntriesService:

    @staticmethod
    async def create_loan_entry(data: LoanEntriesCreate, session: AsyncSession):
        deduction_period: date | None = None
        if not data.calculation_type:
            if data.deduction_start_period_id:
                deduction_period = await PeriodService.get_period(
                    id=data.deduction_start_period_id, session=session
                )
                if not deduction_period:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Period not found"
                    )
                data.deduction_start_period_name = deduction_period.period_name
                data.deduction_start_period_code = deduction_period.period_code
                if isinstance(deduction_period.start_date, date):
                    duration_in_months = math.ceil(data.duration)
                    data.deduction_end_date = (
                        deduction_period.start_date
                        + relativedelta(months=duration_in_months - 1)
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Deduction start period is required",
                    )

        if data.employee_id:
            employee = await EmployeeService.get_employee(
                id=data.employee_id, session=session
            )
            if not employee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
                )
            data.employee_code = employee.code
            data.employee_fullname = employee.fullname
            data.national_id = employee.national_id

        if data.loan_id:
            loan = await LoanService.get_loan(id=data.loan_id, session=session)
            if not loan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found"
                )
            data.code = loan.code
            data.description = loan.name

        loan_entry = LoanEntries.model_validate(data)
        session.add(loan_entry)

        await session.flush()

        await defualt_schedule_generation(
            start_date=deduction_period.start_date,
            loan_id=loan_entry,
            data=data,
            session=session,
        )

        await session.commit()
        await session.refresh(loan_entry)

        return loan_entry

    @staticmethod
    async def get_loan_entries(session: AsyncSession, limit: int = 10, offset: int = 0):
        query = (
            select(LoanEntries)
            .order_by(LoanEntries.id)
            .limit(limit=limit)
            .offset(offset=offset)
        )
        result = await session.exec(query)

        loan_entries = result.unique().all()
        count = len(loan_entries)

        return ResponseModel(count=count, results=loan_entries)

    @staticmethod
    async def get_loan_entry(id: UUID, session: AsyncSession):
        query = select(LoanEntries).where(LoanEntries.id == id)
        result = await session.exec(query)

        loan_entry = result.unique().one_or_none()

        if not loan_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Loan entry not found"
            )

        return loan_entry

    @staticmethod
    async def delete_loan_entry(id: UUID, session: AsyncSession):
        loan_entry = await LoanEntriesService.get_loan_entry(id=id, session=session)
        if not loan_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Loan entry not found"
            )

        setattr(loan_entry, "exclude", True)
        session.add(loan_entry)
        await session.flush()

        await delete_payment_by_loan_entry_id(
            loan_entry_id=loan_entry.id, session=session
        )
        await PaymentScheduleService.delete_schedule_based_on_loan_entry_id(
            loan_entry_id=loan_entry.id, session=session
        )

        await session.commit()

        return {}

    @staticmethod
    async def update_loan_entry(
        id: UUID, data: LoanEntriesUpdate, session: AsyncSession
    ):
        loan_entry = await LoanEntriesService.get_loan_entry(id=id, session=session)
        if not loan_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Loan entry not found"
            )
        for key, value in data.model_dump(exclude_unset=True).items():
            if value:
                setattr(loan_entry, key, value)

        session.add(loan_entry)
        await session.commit()
        await session.refresh(loan_entry)

        return loan_entry
