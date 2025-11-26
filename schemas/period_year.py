from uuid import UUID
from datetime import datetime, date

from sqlmodel import SQLModel


class PeriodYearBase(SQLModel):
    year: int


class PeriodYearCreate(PeriodYearBase):
    pass


class PeriodYearUpdate(PeriodYearBase):
    user_id: UUID | None = None
    updated_at: datetime = datetime.now()


class PeriodYearRead(PeriodYearBase):
    id: int
    user_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class PeriodBase(SQLModel):
    month: int
    year: int
    month_calender: list[list[int]]
    period_code: str
    period_name: str
    start_date: date
    end_date: date
    no_of_days: int
    total_working_days: int
    total_working_hours: int
    total_hours_per_day: int
    period_year_id: int
    user_id: UUID | None = None


class PeriodCreate(PeriodBase):
    pass


class PeriodRead(SQLModel):
    id: UUID
    month: int
    year: int | None = None
    period_code: str
    period_name: str
    start_date: date
    end_date: date
    no_of_days: int
    total_working_days: int
    total_working_hours: int
    total_hours_per_day: int
    period_year_id: int
    user_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class PeriodUpdate(PeriodBase):
    updated_at: datetime = datetime.now()
