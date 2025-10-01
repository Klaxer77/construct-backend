from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

class ErrorResponseModel(BaseModel):
    type: str
    message: str
    details: dict | None = None

class SuccessResponseModel(BaseModel, Generic[T]):
    status: Literal["success"]
    code: int
    data: T

class ErrorEnvelopeModel(BaseModel):
    status: Literal["error"]
    code: int
    error: ErrorResponseModel


