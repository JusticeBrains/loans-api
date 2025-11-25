from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlmodel import (
    DECIMAL,
    Boolean,
    Enum,
    Integer,
    SQLModel,
    Field,
    Column,
    String,
)

from utils.text_options import PaymentType


class PaymentSchedule(SQLModel, table=True):
    __tablename__ = "payment_schedules"
    # __table_args__ = (UniqueConstraint("loan_entry_id", "month"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    loan_entry_id: UUID = Field(foreign_key="loan_entries.id", nullable=False)

    month: int = Field(sa_column=Column(Integer, nullable=False))
    monthly_payment: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False))

    employee_code: str | None = Field(
        sa_column=Column(String(20), nullable=True, default=None)
    )
    employee_fullname: str | None = Field(
        sa_column=Column(String(255), nullable=True, default=None)
    )

    interest: Decimal | None = Field(
        sa_column=Column(DECIMAL(5, 2), nullable=True, default=None)
    )
    balance: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    balance_bf: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )

    fixed_monthly_payment: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    amount_paid: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    difference: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    paid: bool = Field(sa_column=Column(Boolean, default=False))
    is_deleted: bool = Field(sa_column=Column(Boolean, default=False))

    company_id: UUID | None = Field(
        foreign_key="companies.id", nullable=True, default=None
    )
    company_name: str | None = Field(
        sa_column=Column(String(100), nullable=True, default=None)
    )
    user_id: UUID | None = Field(foreign_key="users.id", nullable=True, default=None)
    user_name: str | None = Field(
        sa_column=Column(String(100), nullable=True, default=None)
    )

    modified_by: UUID | None = Field(
        foreign_key="users.id", nullable=True, default=None
    )
    modified_by_name: str | None = Field(
        sa_column=Column(String(100), nullable=True, default=None)
    )

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    loan_entry_id: UUID = Field(foreign_key="loan_entries.id", nullable=False)

    loan_entry_description: str | None = Field(
        sa_column=Column(String(255), nullable=True, default=None)
    )
    loan_entry_name: str | None = Field(
        sa_column=Column(String(255), nullable=True, default=None)
    )
    loan_entry_code: str | None = Field(
        sa_column=Column(String(20), nullable=True, default=None)
    )

    employee_id: UUID | None = Field(
        foreign_key="employees.id", nullable=True, default=None
    )

    employee_code: str | None = Field(
        sa_column=Column(String(20), nullable=True, default=None)
    )
    employee_fullname: str | None = Field(
        sa_column=Column(String(255), nullable=True, default=None)
    )

    amount_paid: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False))
    payment_type: PaymentType = Field(
        sa_column=Column(
            Enum(PaymentType, name="payment_type_enum", native_enum=True),
            nullable=False,
        )
    )

    payment_amount: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    expected_monthly_payment: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    remaining_balance: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    principal_amount: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    loan_amount: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    difference: Decimal | None = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )

    company_id: UUID = Field(foreign_key="companies.id", nullable=True, default=None)

    company_name: str | None = Field(
        sa_column=Column(String(100), nullable=True, default=None)
    )

    user_id: UUID = Field(foreign_key="users.id", nullable=True, default=None)

    user_name: str | None = Field(
        sa_column=Column(String(100), nullable=True, default=None)
    )

    processed: bool = Field(sa_column=Column(Boolean, default=False))
    is_deleted: bool = Field(sa_column=Column(Boolean, default=False))

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
