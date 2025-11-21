import uuid
from random import random
from datetime import datetime
from sqlmodel import Relationship, SQLModel, Field, Column, String, Boolean

from models.company import Company


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, unique=True, primary_key=True, index=True
    )
    username: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    email: str = Field(
        sa_column=Column(String(80), nullable=False, unique=True, index=True)
    )
    firstname: str = Field(sa_column=Column(String(50), nullable=False, index=True))
    lastname: str = Field(sa_column=Column(String(50), nullable=False))
    middlename: str | None = Field(
        sa_column=Column(String(50), nullable=True, default=None)
    )

    password: str = Field(sa_column=Column(String(255), nullable=False))
    pin: str | None = Field(sa_column=Column(String(6), nullable=True, default=None))

    company_id: uuid.UUID = Field(foreign_key="companies.id", nullable=False)
    company: Company = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "joined"}
    )

    employees: list["Employee"] = Relationship(back_populates="user")
    # period_years: list["PeriodYear"] = Relationship(back_populates="users", sa_relationship_kwargs={"lazy": "joined"})
    # periods: list["Period"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "joined"})

    is_active: bool = Field(sa_column=Column(Boolean, nullable=False, default=True))
    is_super: bool = Field(sa_column=Column(Boolean, nullable=False, default=False))

    is_password_changed: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False)
    )
    is_password_reset: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False)
    )

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    @staticmethod
    def get_fullname(data):
        if data.middlename:
            return f"{data.lastname} {data.middlename} {data.firstname}"
        else:
            return f"{data.lastname} {data.firstname}"

    @staticmethod
    def get_username(data):
        ext = str(random())
        return f"{data.firstname[:4].lower()}{data.lastname[1:3].lower()}{ext[3:5]}"

    def __repr__(self):
        return f"{self.username} {self.company.name}"

    def __str__(self):
        return self.__repr__()
