from decimal import Decimal
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models.payment_schedule import Payment
from models.user import User
from schemas.base import ResponseModel
from schemas.payment import PaymentCreate
from uuid import UUID

from schemas.payment_schedule import PaymentScheduleUpdate
from services.company import CompanyService
from services.loan import LoanEntriesService
from services.payment_schedule import PaymentScheduleService

from utils.helper import get_sorted_schedules_and_min_month
from utils.text_options import PaymentType


class PaymentService:
    @staticmethod
    async def create_payment(
        data: PaymentCreate, session: AsyncSession, current_user: User
    ):
        try:
            loan_entry = await LoanEntriesService.get_loan_entry(
                id=data.loan_entry_id, session=session
            )
            if not loan_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Loan entry not found"
                )

            company = None
            if data.company_id:
                company = await CompanyService.get_company(
                    id=data.company_id, session=session
                )
                if not company:
                    raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
                )

            schedules, min_month = await get_sorted_schedules_and_min_month(
                loan_entry_id=loan_entry.id, session=session
            )

            if not min_month:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No payment schedule found for this loan entry",
                )

            payment = Payment.model_validate(data, update={"user_id": current_user.id})
            payment.employee_id = loan_entry.employee_id
            payment.employee_code = loan_entry.employee_code
            payment.employee_fullname = loan_entry.employee_fullname
            payment.loan_amount = loan_entry.amount
            payment.loan_entry_description = loan_entry.description
            payment.loan_entry_code = loan_entry.code
            payment.user_name = current_user.username
            payment.company_name = company.name if company else ""
            payment.company_id = company.id if company else None

            session.add(payment)
            await session.flush()

            if payment.payment_type == PaymentType.Default:
                current_total_payment = (
                    loan_entry.total_amount_paid if loan_entry.total_amount_paid else 0
                )
                expected_monthly_amount = min_month.monthly_payment
                loan_entry.monthly_repayment = expected_monthly_amount

                amount_paid = min(
                    payment.amount_paid or 0, loan_entry.amount - current_total_payment
                )

                schedule_update = PaymentScheduleUpdate(
                    loan_entry_id=loan_entry.id,
                    amount_paid=amount_paid,
                    paid=True,
                    difference=round(amount_paid - expected_monthly_amount, 2),
                    modified_by=current_user.id,
                    modified_by_name=current_user.username,
                )

                await PaymentScheduleService.update_schedule(
                    id=min_month.id, data=schedule_update, session=session
                )

                new_total_paid = round(current_total_payment + amount_paid, 2)
                remaining_amount = round(loan_entry.amount - new_total_paid, 2)
                loan_entry.total_amount_paid = new_total_paid
                loan_entry.remaining_balance = remaining_amount

                payment.remaining_balance = remaining_amount

                if remaining_amount <= 0:
                    loan_entry.closed = True
                    loan_entry.status = False

            elif payment.payment_type == PaymentType.Custom:
                amount_paid = payment.amount_paid
                total_paid = 0

                for schedule in schedules:
                    if amount_paid <= 0:
                        break

                    amount_left = schedule.monthly_payment - (
                        schedule.amount_paid or Decimal(0)
                    )
                    amount_to_pay = min(amount_paid, amount_left)
                    if amount_to_pay <= 0:
                        continue

                    schedule_amount_paid = amount_to_pay + (
                        schedule.amount_paid or Decimal(0)
                    )
                    difference = schedule.monthly_payment - schedule_amount_paid

                    if schedule_amount_paid >= schedule.monthly_payment:
                        processed = True
                    else:
                        processed = False

                    schedule_update = PaymentScheduleUpdate(
                        loan_entry_id=loan_entry.id,
                        amount_paid=schedule_amount_paid,
                        paid=processed,
                        difference=round(difference, 2),
                        month=schedule.month,
                        monthly_payment=schedule.monthly_payment,
                        modified_by=current_user.id,
                        modified_by_name=current_user.username,
                    )
                    await PaymentScheduleService.update_schedule(
                        id=schedule.id, data=schedule_update, session=session
                    )
                    total_paid += amount_to_pay
                    amount_paid -= amount_to_pay

                current_total_payment = loan_entry.total_amount_paid or Decimal(0)
                new_total_payment = current_total_payment + total_paid
                new_remaining = loan_entry.amount - new_total_payment

                loan_entry.total_amount_paid = new_total_payment
                loan_entry.remaining_balance = new_remaining

                if new_total_payment >= loan_entry.amount:
                    loan_entry.status = False
                    loan_entry.closed = True

            await session.commit()
            await session.refresh(payment)

            return payment

        except HTTPException:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating payment: {str(e)}",
            )

    @staticmethod
    async def get_payments(session: AsyncSession, limit: int = 10, offset: int = 0):
        query = (
            select(Payment)
            .order_by(Payment.created_at.desc())
            .limit(limit=limit)
            .offset(offset=offset)
        )
        result = await session.exec(query)

        payments = result.unique().all()
        count = len(payments)

        return ResponseModel(count=count, results=payments)

    @staticmethod
    async def get_payment(id: UUID, session: AsyncSession):
        query = select(Payment).where(Payment.id == id)
        result = await session.exec(query)

        payment = result.unique().one_or_none()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        return payment

    @staticmethod
    async def delete_payment(id: UUID, session: AsyncSession):
        payment = await PaymentService.get_payment(id=id, session=session)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        payment.is_deleted = True

        session.add(payment)
        await session.commit()
        await session.refresh(payment)

        return {}

    @staticmethod
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
