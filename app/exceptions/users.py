from fastapi import status

from app.exceptions.base import BaseHTTPException


class ContractorNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Contractor not found"

class UserMinPasswordErrorExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Minimum password length is 8 characters"

class UserNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found"

class UserIsExistsExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "User is exists"
    
class UserIsExistsWithEmailExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "User with this email already exists"

class InvalidTokenExc(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid token"

class TokenNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Token not found"


class TokenExpiredExc(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Token has expired"


class IncorrectTokenFormatExc(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid token format"


class UserIsNotPresentExc(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Not authorized"


class IncorrectEmailExc(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Incorrect email"
    
class IncorrectPasswordExc(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Incorrect password"
    
class UserSelfDeleteErrorExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "You can't delete yourself"
    
class UserIsNotActivatedExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "User is not activated"
    
class InvalidCoordsUserExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid coords user"