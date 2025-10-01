from fastapi import status

from app.exceptions.base import BaseHTTPException


class ObjectNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Object not found"

class ActObjectIsExistsExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Act object is exists"
    
class ActObjectIsNotExistsExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Act object is not exists"
    
class ActNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Act object not found"
    
class ObjectActNotRequiredExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Object act not required"
    
class ObjectCategoryNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Object category not found"
    
class UserObjectSessionNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "User object session not found"