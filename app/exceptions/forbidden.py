from fastapi import status

from app.exceptions.base import BaseHTTPException


class ForBiddenException(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Resource forbidden"


class PermissionAccessDenied(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Permission access denied"


class AccessDenied(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Access denied"
