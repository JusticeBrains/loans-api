import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, String, DateTime, Relationship


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, unique=True)
    name: str = Field(sa_column=Column(String(100), nullable=False))

    users: list["User"] = Relationship(back_populates="company")
    employees: list["Employee"] = Relationship(back_populates="company", sa_relationship_kwargs={"lazy": "joined"})
    period_years: list["PeriodYear"] = Relationship(back_populates="company", sa_relationship_kwargs={"lazy": "joined"})
    periods: list["Period"] = Relationship(back_populates="company", sa_relationship_kwargs={"lazy": "joined"})

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
