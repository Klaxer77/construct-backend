from fastapi import status

from app.exceptions.base import BaseHTTPException


class CategoryMaterialNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Category material not found"