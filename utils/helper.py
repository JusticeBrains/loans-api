from datetime import date, timedelta
import calendar
import math
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from models.loan import LoanEntries
from models.payment_schedule import Payment, PaymentSchedule
from schemas.loan import LoanEntriesCreate
from schemas.payment_schedule import PaymentScheduleCreate
from services.payment_schedule import PaymentScheduleService

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def count_working_days(start_date, end_date):
    if start_date and end_date:
        total_days = (end_date - start_date).days + 1
        working_days = 0

        for day in range(total_days):
            current_day = start_date + timedelta(days=day)
            if current_day.weekday() < 5:
                working_days += 1

        return working_days


def generate_calender(year):
    cal = calendar.Calendar()
    year_calender = {}

    for month in range(1, 13):
        month_calender = cal.monthdayscalendar(year, month)
        cleaned_onth_calender = [
            [day for day in week if day != 0] for week in month_calender
        ]
        year_calender[month] = cleaned_onth_calender

    return year_calender


def get_days_in_month(year: int, month: int):
    return calendar.monthrange(year, month)[1]


async def defualt_schedule_generation(
    start_date: date,
    loan_id: LoanEntries,
    data: LoanEntriesCreate,
    session: AsyncSession,
):
    if isinstance(start_date, date):
        if data.amount and data.monthly_repayment:
            duration = data.amount / data.monthly_repayment
            data.duration = duration
            data.monthly_repayment = data.amount / duration

        if data.amount and data.duration:
            data.monthly_repayment = data.amount / data.duration

        if data.amount and data.duration and data.monthly_repayment:
            amount_left = data.amount
            for month in range(1, math.ceil(data.duration) + 1):
                monthly_amount = min(amount_left, data.monthly_repayment)
                amount_left = round(amount_left - monthly_amount, 4)
                await PaymentScheduleService.create_schedule(
                    data=PaymentScheduleCreate(
                        loan_entry_id=loan_id.id,
                        month=month,
                        employee_id=loan_id.employee_id,
                        employee_code=loan_id.employee_code,
                        employee_fullname=loan_id.employee_fullname,
                        monthly_payment=monthly_amount,
                        balance_bf=amount_left + monthly_amount,
                        balance=amount_left,
                        # company_id=loan_id.company_id,
                        # company_name=loan_id.company_name,
                        user_id=loan_id.user_id,
                        # user_name=loan_id.user_name,
                    ),
                    session=session,
                )
                if amount_left <= 0:
                    break


async def get_sorted_schedules_and_min_month(
    loan_entry_id: UUID, session: AsyncSession
) -> tuple[list[PaymentSchedule], PaymentSchedule]:
    query = (
        select(PaymentSchedule)
        .where(PaymentSchedule.loan_entry_id == loan_entry_id)
        .order_by(PaymentSchedule.month.asc())
    )
    schedules = await session.exec(query)
    schedules = schedules.unique().all()
    min_month = schedules[0]
    return schedules, min_month


async def delete_payment_by_loan_entry_id(
        loan_entry_id: UUID, session: AsyncSession
    ):
        query = select(Payment).where(Payment.loan_entry_id == loan_entry_id)
        result = await session.exec(query)

        payments = result.unique().all()

        for payment in payments:
            payment.is_deleted = True
            session.add(payment)

        session.commit()
        session.refresh(payments)

        return {}