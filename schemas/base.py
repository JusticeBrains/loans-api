from typing import Generic, List, TypeVar
from sqlmodel import SQLModel

T = TypeVar("T")

class ResponseModel(SQLModel, Generic[T]):
    count: int
    next: str | None = None
    previous: str | None = None
    results: List[T]
