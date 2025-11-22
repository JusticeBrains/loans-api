from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import SQLModel


class PaymentScheduleBase(SQLModel):
    loan_entry_id: UUID
    month: int
    monthly_payment: Decimal
    employee_code: str | None = None
    employee_fullname: str | None = None
    interest: Decimal | None = None
    balance: Decimal | None = None
    balance_bf: Decimal | None = None
    fixed_monthly_payment: Decimal | None = None
    amount_paid: Decimal | None = None
    difference: Decimal | None = None
    paid: bool = False
    is_deleted: bool = False
    # company_id: UUID


class PaymentScheduleCreate(PaymentScheduleBase):
    company_name: str | None = None


class PaymentScheduleRead(PaymentScheduleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class PaymentScheduleUpdate(PaymentScheduleBase):
    pass
