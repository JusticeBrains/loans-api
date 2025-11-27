from datetime import date
import math
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from dateutil.relativedelta import relativedelta

from models.loan import Loan, LoanEntries
from models.period_year import Period
from models.user import User
from schemas.base import ResponseModel
from schemas.loan import LoanCreate, LoanEntriesCreate, LoanEntriesUpdate, LoanUpdate
from services.company import CompanyService
from services.employee import EmployeeService
from services.payment_schedule import PaymentScheduleService
from utils.helper import defualt_schedule_generation, delete_payment_by_loan_entry_id
from utils.text_options import InterestCalculationType, InterestTerm


class LoanService:
    @staticmethod
    async def create_loan(data: LoanCreate, session: AsyncSession, current_user: User):
        try:
            data = data.model_dump()
            data["user_id"] = current_user.id
            loan = Loan.model_validate(data)

            session.add(loan)
            await session.commit()
            await session.refresh(loan)

            return loan
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

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
    async def get_loans(
        session: AsyncSession,
        code: str | None = None,
        name: str | None = None,
        interest_term: InterestTerm | None = None,
        calculation_type: InterestCalculationType | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        query = (
            select(Loan).order_by(Loan.name).limit(limit=limit).offset(offset=offset)
        )
        if code:
            query = query.where(Loan.code == code)
        if name:
            query = query.where(Loan.name == name)
        if interest_term:
            query = query.where(Loan.interest_term == interest_term)
        if calculation_type:
            query = query.where(Loan.calculation_type == calculation_type)
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
    async def update_loan(
        id: UUID, data: LoanUpdate, session: AsyncSession, current_user: User
    ):
        loan = await LoanService.get_loan(id=id, session=session)
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found"
            )
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(loan, key, value)

        loan["modified_by_id"] = current_user.id
        session.add(loan)
        await session.commit()
        await session.refresh(loan)

        return loan


class LoanEntriesService:
    @staticmethod
    async def create_loan_entry(
        data: LoanEntriesCreate, session: AsyncSession, current_user: User
    ):
        try:
            deduction_period: date | None = None

            if data.employee_id:
                employee = await EmployeeService.get_employee(
                    id=data.employee_id, session=session
                )
                if not employee:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Employee not found",
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
                data.loan_name = loan.name

            if data.company_id:
                company = await CompanyService.get_company(
                    id=data.company_id, session=session
                )
                if not company:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Company not found",
                    )
                data.company_name = company.name

            data.user_id = current_user.id

            loan_entry = LoanEntries.model_validate(data)
            session.add(loan_entry)

            await session.flush()

            if data.deduction_start_period_id:
                deduction_period = await session.get(
                    Period, data.deduction_start_period_id
                )
                if not deduction_period:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Period not found",
                    )
                loan_entry.deduction_start_period_name = deduction_period.period_name
                loan_entry.deduction_start_period_code = deduction_period.period_code

            duration = await defualt_schedule_generation(
                start_date=deduction_period.start_date,
                loan_id=loan_entry.id,
                data=data,
                session=session,
            )

            loan_entry.duration = duration

            if duration:
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

            await session.commit()
            await session.refresh(loan_entry)

            return loan_entry
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def get_loan_entries(
        session: AsyncSession,
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
        limit: int = 10,
        offset: int = 0,
    ):
        query = (
            select(LoanEntries)
            .order_by(LoanEntries.id)
            .limit(limit=limit)
            .offset(offset=offset)
        )
        if id:
            query = query.where(LoanEntries.id == id)
        if code:
            query = query.where(LoanEntries.code == code)
        if employee_id:
            query = query.where(LoanEntries.employee_id == employee_id)
        if employee_code:
            query = query.where(LoanEntries.employee_code == employee_code)
        if employee_fullname:
            query = query.where(LoanEntries.employee_fullname == employee_fullname)
        if national_id:
            query = query.where(LoanEntries.national_id == national_id)
        if loan_id:
            query = query.where(LoanEntries.loan_id == loan_id)
        if loan_name:
            query = query.where(LoanEntries.loan_name == loan_name)
        if description:
            query = query.where(LoanEntries.description == description)
        if interest_term:
            query = query.where(LoanEntries.interest_term == interest_term)
        if calculation_type:
            query = query.where(LoanEntries.calculation_type == calculation_type)
        # if company_id:
        #     query = query.where(LoanEntries.company_id == company_id)
        if exclude:
            query = query.where(LoanEntries.exclude == exclude)
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

        setattr(loan_entry, "is_deleted", True)
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
        id: UUID, data: LoanEntriesUpdate, session: AsyncSession, current_user: User
    ):
        loan_entry = await LoanEntriesService.get_loan_entry(id=id, session=session)
        if not loan_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Loan entry not found"
            )
        for key, value in data.model_dump(exclude_unset=True).items():
            if value:
                setattr(loan_entry, key, value)

        loan_entry["modified_by_id"] = current_user.id
        session.add(loan_entry)
        await session.commit()
        await session.refresh(loan_entry)

        return loan_entry
