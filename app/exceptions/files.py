from fastapi import status

from app.exceptions.base import BaseHTTPException


class FileLimitSizeExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Limit size file 20MB"

class ActFileNotUploadedExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Act file not uploaded"