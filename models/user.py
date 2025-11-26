import uuid
from random import random
from datetime import datetime
from sqlmodel import Integer, SQLModel, Field, Column, String, Boolean


from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: str = Field(
        sa_column=Column(String(50), nullable=False, unique=True, index=True)
    )
    email: str = Field(
        sa_column=Column(String(80), nullable=False, unique=True, index=True)
    )
    firstname: str = Field(sa_column=Column(String(50), nullable=False, index=True))
    lastname: str = Field(sa_column=Column(String(50), nullable=False))
    middlename: Optional[str] = Field(
        sa_column=Column(String(50), nullable=True), default=None
    )
    fullname: Optional[str] = Field(
        sa_column=Column(String(100), nullable=True), default=None
    )
    password: str = Field(sa_column=Column(String(255), nullable=False))
    pin: Optional[str] = Field(sa_column=Column(String(6), nullable=True), default=None)
    company_id: Optional[uuid.UUID] = Field(
        foreign_key="companies.id", nullable=True, default=None
    )
    is_active: int = Field(sa_column=Column(Integer, nullable=False, default=1))
    is_super: int = Field(sa_column=Column(Integer, nullable=False, default=0))
    is_password_changed: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False)
    )
    is_password_reset: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False)
    )
    created_at: datetime = Field(default_factory=datetime.now, nullable=True)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        nullable=True,
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
        return f"{self.username}"

    def __str__(self):
        return self.__repr__()


class RevokedToken(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    token: str = Field(
        sa_column=Column(String(255), nullable=False, index=True, unique=True)
    )
    revoked_at: datetime = Field(default_factory=datetime.now)
