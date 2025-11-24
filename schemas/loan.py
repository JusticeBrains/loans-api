from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from pydantic.v1 import NoneStr
from sqlmodel import SQLModel

from models.loan import Loan
from utils.text_options import InterestCalculationType, InterestTerm


class LoanBase(SQLModel):
    code: str
    name: str
    interest_term: InterestTerm
    calculation_type: InterestCalculationType
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    interest_rate: Decimal | None = None
    exclude: bool | None = False
    company_id: UUID
    user_id: UUID


class LoanCreate(LoanBase):
    pass


class LoanRead(LoanBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class LoanUpdate(SQLModel):
    code: str | None = None
    name: str | None = None
    interest_term: str | None = None
    calculation_type: str | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    interest_rate: Decimal | None = None
    company_id: UUID | None = NoneStr
    modified_by_id: UUID | None = None


class LoanEntriesBase(SQLModel):
    code: str | None = None
    loan_id: UUID
    description: str | None = None
    loan_name: str | None = None
    amount: Decimal
    employee_id: UUID
    employee_code: str | None = None
    employee_fullname: str | None = None
    national_id: str | None = None
    user_id: UUID
    calculation_type: InterestCalculationType | None = None
    interest_term: InterestTerm | None = None
    periodic_principal: Decimal | None = None
    monthly_repayment: Decimal | None = None
    interest_rate: Decimal | None = None
    remaining_balance: Decimal | None = None
    total_amount_paid: Decimal | None = None
    duration: Decimal | None = None
    deduction_start_period_id: UUID
    deduction_start_period_name: str | None = None
    deduction_start_period_code: str | None = None
    deduction_end_date: date | None = None
    closed: bool = False
    status: bool = True
    exclude: bool = False


class LoanEntriesCreate(LoanEntriesBase):
    pass


class LoanEntriesUpdate(LoanEntriesBase):
    pass


class LoanEntriesRead(LoanEntriesBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
