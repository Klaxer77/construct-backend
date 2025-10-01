from fastapi import status

from app.exceptions.base import BaseHTTPException


class LLMErrorExc(BaseHTTPException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    message = "LLM error"