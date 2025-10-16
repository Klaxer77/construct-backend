from fastapi import status

from app.exceptions.base import BaseHTTPException


class ObjectNFCUidIsExistsExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Object NFC uid is exists"
    
class NFCNotFoundExc(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "NFC not found"
    
class NFCLabelIsExistsExc(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "NFC label is exists"