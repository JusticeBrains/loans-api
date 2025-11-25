from uuid import UUID, uuid4

from datetime import datetime, date
from sqlmodel import (
    JSON,
    Column,
    Identity,
    Integer,
    SQLModel,
    Field,
    Date,
    String,
    UniqueConstraint,
)


from models.company import Company


class PeriodYear(SQLModel, table=True):
    __tablename__ = "period_years"
    __table_args__ = (UniqueConstraint("year", "company_id"),)

    id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            Identity(
                always=False,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            primary_key=True,
            nullable=False,
        ),
    )
    year: int = Field(sa_column=Column(Integer, nullable=False))

    company_id: UUID = Field(foreign_key="companies.id", nullable=False, index=True)

    user_id: UUID | None = Field(foreign_key="users.id", nullable=True, default=None)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )


class Period(SQLModel, table=True):
    __tablename__ = "periods"

    id: UUID = Field(default_factory=uuid4, unique=True, primary_key=True, index=True)
    month: int = Field(sa_column=Column(Integer, nullable=False))
    month_calender: list[list[int]] = Field(sa_column=Column(JSON, nullable=True))
    year: int | None = Field(sa_column=Column(Integer, nullable=True))

    period_code: str = Field(sa_column=Column(String(10), nullable=False))
    period_name: str = Field(sa_column=Column(String(20), nullable=False))

    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))

    no_of_days: int = Field(sa_column=Column(Integer, nullable=False))
    total_working_days: int = Field(sa_column=Column(Integer, nullable=False))
    total_working_hours: int = Field(sa_column=Column(Integer, nullable=False))
    total_hours_per_day: int = Field(sa_column=Column(Integer, nullable=False))

    company_id: UUID = Field(foreign_key="companies.id", nullable=False, index=True)

    period_year_id: int = Field(
        foreign_key="period_years.id", nullable=False, index=True
    )

    user_id: UUID | None = Field(foreign_key="users.id", nullable=True, default=None)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
