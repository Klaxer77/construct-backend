import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import RemarkActionEnum, RemarkStatusEnum


class SRemarkChangeStatus(BaseModel):
    action: RemarkActionEnum

class SRemarkCreate(BaseModel):
    violations: str
    name_regulatory_docx: str
    expiration_date: datetime
    comment: str | None = None
    photos_keys: list[str] = []   # точные имена файлов, например "photo1.png"

    model_config = ConfigDict(from_attributes=True)
    
class SRemark(SRemarkCreate):
    id: uuid.UUID
    status: RemarkStatusEnum
    
    model_config = ConfigDict(from_attributes=True)
    
    
class SRemarksList(BaseModel):
    id: uuid.UUID
    object_name: str
    responsible_user_name: str | None
    status: RemarkStatusEnum
    date_remark: datetime
    expiration_date: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SRemarkPhotos(BaseModel):
    file_path: str
    
class SRemarkAnswerPhotos(BaseModel):
    file_path: str
    
class SRemarkChangedSuccess(BaseModel):
    result: str
    
class SRemarkAnswerCreate(BaseModel):
    comment: str | None = None


class SRemarkAnswerFile(BaseModel):
    file_path: str

    model_config = ConfigDict(from_attributes=True)


class SRemarkAnswer(BaseModel):
    id: uuid.UUID
    comment: str | None
    created_at: datetime
    files: list[SRemarkAnswerFile]

    model_config = ConfigDict(from_attributes=True)
    
class SRemarkSubDetail(BaseModel):
    id: uuid.UUID
    violations: str
    name_regulatory_docx: str
    comment: str | None
    status: RemarkStatusEnum
    expiration_date: datetime
    photos: list[SRemarkPhotos]
    answer: SRemarkAnswer | None 
    
class SRemarksDetail(BaseModel):
    id: uuid.UUID
    status: RemarkStatusEnum
    date_remark: datetime
    expiration_date: datetime
    object_name: str
    remarks: list[SRemarkSubDetail]