import calendar
import time
from tracemalloc import start
from uuid import UUID, uuid4

from datetime import datetime, date, timedelta
from sqlmodel import JSON, Column, Integer, Relationship, SQLModel, Field, Date, String, null

from models.company import Company


class PeriodYear(SQLModel, table=True):
    __tablename__ = "period_years"

    id: UUID = Field(default_factory=uuid4, unique=True, primary_key=True, index=True)
    year: int = Field(sa_column=Column(Integer, nullable=False))

    company_id: UUID = Field(foreign_key="companies.id", nullable=False, index=True)
    company: Company = Relationship(
        back_populates="period_years", sa_relationship_kwargs={"lazy": "joined"}
    )

    user_id: UUID | None = Field(foreign_key="users.id",nullable=True, default=None)


    periods: list["Period"] = Relationship(back_populates="period_year", sa_relationship_kwargs={"lazy": "joined"})
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )


    


class Period(SQLModel, table=True):
    __tablename__ = "periods"

    id: UUID = Field(default_factory=uuid4, unique=True, primary_key=True, index=True)
    month: int = Field(sa_column=Column(Integer, nullable=False))
    month_calender: list[list[int]] = Field(sa_column=Column(JSON, nullable=False))
    year: int = Field(sa_column=Column(Integer, nullable=False))
    
    period_code: str = Field(sa_column=Column(String(10), nullable=False))
    period_name:str = Field(sa_column=Column(String(20), nullable=False))
    
    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))

    no_of_days: int = Field(sa_column=Column(Integer, nullable=False))
    total_working_days: int = Field(sa_column=Column(Integer, nullable=False))
    total_working_hours: int = Field(sa_column=Column(Integer, nullable=False))
    total_hours_per_day: int = Field(sa_column=Column(Integer, nullable=False))

    company_id: UUID = Field(foreign_key="companies.id", nullable=False, index=True)
    company: Company = Relationship(
        back_populates="periods", sa_relationship_kwargs={"lazy": "joined"}
    )

    period_year_id: UUID = Field(foreign_key="period_years.id", nullable=False, index=True)
    period_year: PeriodYear = Relationship(
        back_populates="periods", sa_relationship_kwargs={"lazy": "joined"}
    )

    user_id: UUID | None = Field(foreign_key="users.id", nullable=True, default=None)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
