import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ActStatusEnum, DocumentStatusEnum, ObjectStatusesEnum, ObjectTypeEnum
from app.schemas.company import ResponsibleUserSub
from app.schemas.users import SUserCurrentSubObject


class SActdocumentDetail(BaseModel):
    id: uuid.UUID
    code: str
    title: str
    status: DocumentStatusEnum
    description: str
    
    model_config = ConfigDict(from_attributes=True)
class SActDetail(BaseModel):
    id: uuid.UUID
    file_url: str | None
    status: ActStatusEnum
    date_verification: datetime
    responsible_fio: str | None = None
    contractor_title: str | None = None
    documents: list[SActdocumentDetail]
    
    model_config = ConfigDict(from_attributes=True)

class SObjectCreate(BaseModel):
    general_info: str
    title: str
    city: str
    date_delivery_verification: datetime
    start_date: datetime
    coords: list[tuple[float, float]] | list[list[tuple[float, float]]]
    
    model_config = ConfigDict(from_attributes=True)
    
class SObjectUpdated(BaseModel):
    id: uuid.UUID
    using_id: str
    status: ObjectStatusesEnum
    object_type: ObjectTypeEnum
    created_at: datetime
    updated_at: datetime
    general_info: str
    title: str
    city: str
    date_delivery_verification: datetime
    start_date: datetime
    
    model_config = ConfigDict(from_attributes=True)    
    
class SObject(SObjectCreate):
    id: uuid.UUID
    using_id: str
    status: ObjectStatusesEnum
    object_type: ObjectTypeEnum
    created_at: datetime
    updated_at: datetime
    
    
    model_config = ConfigDict(from_attributes=True)
    
class SObjectDetail(BaseModel):
    id: uuid.UUID
    using_id: str
    status: ObjectStatusesEnum
    object_type: ObjectTypeEnum
    created_at: datetime
    updated_at: datetime
    general_info: str
    title: str
    city: str
    date_delivery_verification: datetime
    start_date: datetime
    coords: list[tuple[float, float]] | list[list[tuple[float, float]]]
    responsible_user: SUserCurrentSubObject | None
    
    model_config = ConfigDict(from_attributes=True)   
     
class SCountObjects(BaseModel):
    count: int
    
    model_config = ConfigDict(from_attributes=True)
    
class SCategoriesObjects(BaseModel):
    id: uuid.UUID
    title: str
    
    model_config = ConfigDict(from_attributes=True)
    
class SActObjectSub(BaseModel):
    status: ActStatusEnum
    file_url: str | None
    
    model_config = ConfigDict(from_attributes=True)
    
class SObjectsList(BaseModel):
    id: uuid.UUID
    using_id: str
    status: ObjectStatusesEnum
    object_type: ObjectTypeEnum
    title: str
    general_info: str
    responsible_user_id: uuid.UUID | None
    city: str
    date_delivery_verification: datetime
    responsible_user: ResponsibleUserSub | None
    act: SActObjectSub | None
    is_nfc: bool
    
    model_config = ConfigDict(from_attributes=True)
    

class ActDocxCreate(BaseModel):
    code: str
    title: str
    description: str
    status: DocumentStatusEnum
    
    model_config = ConfigDict(from_attributes=True)
    
class SActDocx(ActDocxCreate):
    id: uuid.UUID
    description: str
    
    model_config = ConfigDict(from_attributes=True)
        
class SActCreate(BaseModel):
    contractor_id: uuid.UUID  
    date_verification: datetime 
    act_docx: list[ActDocxCreate]
    
    model_config = ConfigDict(from_attributes=True)
    
class SAct(SActCreate):
    id: uuid.UUID
    file_url: str | None
    status: ActStatusEnum
    act_docx: SActDocx
    
    model_config = ConfigDict(from_attributes=True)
    
class SActSuccessCreated(BaseModel):
    id: uuid.UUID
    file_url: str | None
    status: ActStatusEnum
    date_verification: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class SObjectGEOCheck(BaseModel):
    result: str