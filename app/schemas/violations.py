import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ViolationActionEnum, ViolationStatusEnum


class SViolationChangeStatus(BaseModel):
    action: ViolationActionEnum

class SViolationCreate(BaseModel):
    violations: str
    name_regulatory_docx: str
    expiration_date: datetime
    comment: str | None = None
    photos_keys: list[str] = []   # точные имена файлов, например "photo1.png"

    model_config = ConfigDict(from_attributes=True)
    
class SViolation(SViolationCreate):
    id: uuid.UUID
    status: ViolationStatusEnum
    
    model_config = ConfigDict(from_attributes=True)
    
    
class SViolationsList(BaseModel):
    id: uuid.UUID
    object_name: str
    responsible_user_name: str | None
    status: ViolationStatusEnum
    date_violation: datetime
    expiration_date: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SViolationPhotos(BaseModel):
    file_path: str
    
class SViolationChangedSuccess(BaseModel):
    result: str
    
class SVialationAnswerCreate(BaseModel):
    comment: str | None = None
    
class SVialationAnswerFile(BaseModel):
    file_path: str

    model_config = ConfigDict(from_attributes=True)
    
class SVialationAnswer(BaseModel):
    id: uuid.UUID
    comment: str | None
    created_at: datetime
    files: list[SVialationAnswerFile]

    model_config = ConfigDict(from_attributes=True)

class SViolationSubDetail(BaseModel):
    id: uuid.UUID
    violations: str
    name_regulatory_docx: str
    comment: str | None
    status: ViolationStatusEnum
    expiration_date: datetime
    photos: list[SViolationPhotos]  
    answer: SVialationAnswer | None 
    
class SViolationsDetail(BaseModel):
    id: uuid.UUID
    status: ViolationStatusEnum
    date_violation: datetime
    expiration_date: datetime
    object_name: str
    violations: list[SViolationSubDetail]