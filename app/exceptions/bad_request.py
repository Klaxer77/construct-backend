from fastapi import status

from app.exceptions.base import BaseHTTPException


class BadRequestException(BaseHTTPException):
    def __init__(self, message: str):
        super().__init__()
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = message
