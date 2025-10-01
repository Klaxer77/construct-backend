from fastapi import status

from app.exceptions.base import BaseHTTPException


class CompanyNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Company not found"