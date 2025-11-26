from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlmodel import (
    Boolean,
    Date,
    SQLModel,
    String,
    Field,
    Column,
    Enum,
    DECIMAL,
)


from utils.text_options import InterestCalculationType, InterestTerm


class Loan(SQLModel, table=True):
    __tablename__ = "loans"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    code: str = Field(
        sa_column=Column(String(20), nullable=False, index=True, unique=True)
    )
    name: str = Field(sa_column=Column(String(100), nullable=False))

    interest_term: InterestTerm | None = Field(
        default=None,
        sa_column=Column(
            Enum(
                InterestTerm,
                name="interest_term_enum",
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=True,
            default=None,
        ),
    )
    calculation_type: InterestCalculationType | None = Field(
        default=None,
        sa_column=Column(
            Enum(
                InterestCalculationType,
                name="interest_calculation_type_enum",
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=True,
            default=None,
        ),
    )

    min_amount: Decimal = Field(
        default=None, sa_column=Column(DECIMAL(5, 2), nullable=True, default=None)
    )
    max_amount: Decimal = Field(
        default=None, sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    interest_rate: Decimal = Field(
        default=None, sa_column=Column(DECIMAL(5, 2), nullable=True, default=None)
    )

    company_id: UUID | None = Field(
        foreign_key="companies.id", nullable=True, default=None
    )

    user_id: UUID | None = Field(
        foreign_key="users.id", nullable=True, index=True, default=None
    )

    modified_by_id: UUID | None = Field(
        foreign_key="users.id", nullable=True, default=None
    )

    exclude: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )


class LoanEntries(SQLModel, table=True):
    __tablename__ = "loan_entries"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    code: str = Field(sa_column=Column(String(20), nullable=True, default=None))

    loan_id: UUID = Field(foreign_key="loans.id", nullable=False)

    loan_name: str = Field(sa_column=Column(String(255), nullable=False))
    description: str = Field(sa_column=Column(String(255), nullable=True, default=None))
    amount: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False))

    employee_id: UUID = Field(foreign_key="employees.id", nullable=True, default=None)

    employee_code: str | None = Field(
        default=None, sa_column=Column(String(20), nullable=True, default=None)
    )
    employee_fullname: str | None = Field(
        default=None, sa_column=Column(String(255), nullable=True, default=None)
    )
    national_id: str | None = Field(
        default=None, sa_column=Column(String(20), nullable=True, default=None)
    )
    company_id: UUID | None = Field(
        foreign_key="companies.id", nullable=True, default=None
    )
    company_name: str | None = Field(
        default=None, sa_column=Column(String(255), nullable=True, default=None)
    )

    user_id: UUID | None = Field(foreign_key="users.id", nullable=True, default=None)

    modified_by_id: UUID | None = Field(
        foreign_key="users.id", nullable=True, default=None
    )

    calculation_type: InterestCalculationType | None = Field(
        default=None,
        sa_column=Column(
            Enum(
                InterestCalculationType,
                name="interest_calculation_type_enum",
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=True,
            default=None,
        )
    )
    interest_term: InterestTerm | None = Field(
        default=None,
        sa_column=Column(
            Enum(
                InterestTerm,
                name="interest_term_enum",
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=True,
            default=None,
        )
    )

    periodic_principal: Decimal | None = Field(
        default=None, sa_column=Column(DECIMAL(7, 2), nullable=True, default=None)
    )
    monthly_repayment: Decimal | None = Field(
        default=None, sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    interest_rate: Decimal | None = Field(
        default=None, sa_column=Column(DECIMAL(5, 2), nullable=True, default=None)
    )
    remaining_balance: Decimal | None = Field(
        default=None, sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    total_amount_paid: Decimal | None = Field(
        default=None, sa_column=Column(DECIMAL(10, 2), nullable=True, default=None)
    )
    duration: Decimal | None = Field(
        default=None, sa_column=Column(DECIMAL(5, 2), nullable=True, default=None)
    )

    deduction_start_period_id: UUID = Field(foreign_key="periods.id", nullable=False)

    deduction_start_period_name: str = Field(
        sa_column=Column(String(20), nullable=True)
    )
    deduction_start_period_code: str = Field(
        sa_column=Column(String(20), nullable=True)
    )

    deduction_end_date: date | None = Field(sa_column=Column(Date, nullable=True))

    closed: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    status: bool = Field(default=True, sa_column=(Column(Boolean, default=True)))
    exclude: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    is_deleted: bool = Field(default=False, sa_column=Column(Boolean, default=False))

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
