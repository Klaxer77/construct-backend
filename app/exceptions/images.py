from fastapi import status

from app.exceptions.base import BaseHTTPException


class ImageLimitSizeExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Limit size image 10MB"
