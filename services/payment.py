from unittest import result
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models.payment_schedule import Payment
from schemas import payment
from schemas.base import ResponseModel
from schemas.payment import PaymentCreate
from uuid import UUID

from services.company import CompanyService
from services.loan import LoanEntriesService
from services.payment_schedule import PaymentScheduleService
from services.user import UserService
from utils.helper import get_sorted_schedules_and_min_month
from utils.text_options import PaymentType


class PaymentService:
    @staticmethod
    async def create_payment(data: PaymentCreate, session: AsyncSession):
        try:

            loan_entry = await LoanEntriesService.get_loan_entry(
                id=data.loan_entry_id, session=session
            )
            if not loan_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Loan entry not found"
                )
            
            user = await UserService.get_user(id=data.user_id, session=session)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            company = await CompanyService.get_company(id=data.company_id, session=session)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )
            
            # Get sorted schedules
            sorted_schedules, min_month = await get_sorted_schedules_and_min_month(
                loan_entry_id=loan_entry.id, session=session
            )
            
            if not min_month:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No payment schedule found for this loan entry"
                )
            
            payment = Payment.model_validate(data)
            payment.employee_id = loan_entry.employee_id
            payment.employee_code = loan_entry.employee_code
            payment.employee_fullname = loan_entry.employee_fullname
            payment.loan_amount = loan_entry.amount
            payment.loan_entry_description = loan_entry.description
            payment.loan_entry_code = loan_entry.code
            payment.user_name = user.username
            payment.company_name = company.name
            
            session.add(payment)
            await session.flush()
            
            if payment.payment_type == PaymentType.DEFAULT:
                current_total_payment = (
                    loan_entry.total_amount_paid 
                    if loan_entry.total_amount_paid 
                    else 0
                )
                expected_monthly_amount = min_month.monthly_payment
                loan_entry.monthly_repayment = expected_monthly_amount
                
                amount_paid = min(
                    payment.amount_paid or 0,
                    loan_entry.amount - current_total_payment
                )
                
                payment.difference = round(amount_paid - expected_monthly_amount, 2)
                payment.processed = True
                payment.amount_paid = amount_paid
                
                new_total_paid = round(current_total_payment + amount_paid, 2)
                loan_entry.total_amount_paid = new_total_paid
                loan_entry.remaining_balance = round(
                    loan_entry.amount - new_total_paid, 2
                )
                
                if loan_entry.remaining_balance <= 0:
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
                detail=f"Error creating payment: {str(e)}"
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
