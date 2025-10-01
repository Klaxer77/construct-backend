from fastapi import status

from app.exceptions.base import BaseHTTPException


class ViolationNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Violation not found"
    
class ViolationAnswerIsExistsExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Violation answer is exists"