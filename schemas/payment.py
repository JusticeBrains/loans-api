from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlmodel import SQLModel

from utils.text_options import PaymentType


class PaymentBase(SQLModel):
    loan_entry_id: UUID
    loan_entry_description: str | None = None
    loan_entry_code: str | None = None
    employee_id: UUID | None = None
    employee_code: str | None = None
    employee_fullname: str | None = None
    amount_paid: Decimal
    payment_type: PaymentType
    payment_amount: Decimal | None = None
    expected_monthly_payment: Decimal | None = None
    remaining_balance: Decimal | None = None
    principal_amount: Decimal | None = None
    loan_amount: Decimal | None = None
    difference: Decimal | None = None
    processed: bool = False

    company_id: UUID
    company_name: str | None = None
    user_id: UUID
    user_name: str | None = None
    is_deleted: bool = False


class PaymentRead(PaymentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    updated_at: datetime = datetime.now()
