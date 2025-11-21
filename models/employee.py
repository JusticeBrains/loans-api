import uuid
from datetime import datetime

from sqlmodel import Relationship, SQLModel, Field, Column, String, null

from models.company import Company
from models.user import User


class Employee(SQLModel, table=True):
    __tablename__ = "employees"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, unique=True, primary_key=True, index=True
    )
    code: str = Field(sa_column=Column(String(15), nullable=False, unique=True))
    firstname: str = Field(sa_column=Column(String(80), nullable=False, index=True))
    lastname: str = Field(sa_column=Column(String(80), nullable=False))
    middlename: str | None = Field(sa_column=Column(String(80), nullable=True))
    fullname: str = Field(sa_column=Column(String(150), nullable=False))
    company_id: uuid.UUID = Field(foreign_key="companies.id", nullable=False)
    
    company: Company = Relationship(
        back_populates="employees", sa_relationship_kwargs={"lazy": "joined"}
    )

    user_id: uuid.UUID | None = Field(foreign_key="users.id", nullable=True)
    user: User = Relationship(
        back_populates="employees", sa_relationship_kwargs={"lazy": "joined"}
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
