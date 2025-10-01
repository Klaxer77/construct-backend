from fastapi import status

from app.exceptions.base import BaseHTTPException


class RemarkNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Remark not found"
    
class RemarkAnswerIsExistsExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Remark answer is exists"