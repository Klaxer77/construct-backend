from fastapi import HTTPException, status

from app.schemas.base import ErrorResponseModel


class BaseHTTPException(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Internal server error"
    details: dict | None = None

    def __init__(self, message: str | None = None, details: dict | None = None):
        super().__init__(status_code=self.status_code, detail=message or self.message)
        if message:
            self.message = message
        if details:
            self.details = details

    def to_error_response(self) -> ErrorResponseModel:
        return ErrorResponseModel(
            type=self.__class__.__name__,
            message=self.message,
            details=self.details
        )
        
class RateLimitExceededHTTP(BaseHTTPException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Too many requests, please try again later"
    
class TransmissionError(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Nothing was transmitted"