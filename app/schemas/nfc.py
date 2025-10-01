import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SNFCCreate(BaseModel):
    nfc_uid: str
    
    model_config = ConfigDict(from_attributes=True)
    
class SNFC(SNFCCreate):
    id: uuid.UUID
    label: str
    
    model_config = ConfigDict(from_attributes=True)
    
class SNFCVerify(BaseModel):
    access_expires_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class SNFCDelete(BaseModel):
    result: str
    
    model_config = ConfigDict(from_attributes=True)    
    
class SNFCADD(BaseModel):
    access_expires_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class SNFCSessionTerminate(BaseModel):
    result: str
    
    model_config = ConfigDict(from_attributes=True)
    
class NFCLabelScan(BaseModel):
    label: str
    scanned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SNFCHistoryDate(BaseModel):
    date: date
    scans: list[NFCLabelScan]


class SNFCHistoryObject(BaseModel):
    title: str
    using_id: str
    data: list[SNFCHistoryDate]

    model_config = ConfigDict(from_attributes=True)
    
    
class SNFCHistoryObjectList(BaseModel):
    id: uuid.UUID
    nfc_uid: str
    label: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)