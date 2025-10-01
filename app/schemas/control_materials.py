import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SLlmResult(BaseModel):
    sender: str | None = None
    date: str | None = None
    request_number: str | None = None
    receiver: str | None = None
    item_name: str | None = None
    size: str | None = None
    quantity: str | None = None
    net_weight: str | None = None
    gross_weight: str | None = None
    volume: str | None = None
    carrier: str | None = None
    vehicle: str | None = None
    
    model_config = ConfigDict(from_attributes=True)
    
    def replace_nulls(self):
        """Заменяем None на пустую строку"""
        for field, value in self.__dict__.items():
            if value is None:
                setattr(self, field, "")


class SLlmResponse(BaseModel):
    llmResult: SLlmResult | None = None

    model_config = ConfigDict(from_attributes=True)
    
    
class SCreateMaterials(BaseModel):
    sender: str
    date: date
    request_number: str
    receiver: str
    item_name: str
    size: str
    quantity: str
    net_weight: str
    gross_weight: str
    volume: str
    carrier: str
    vehicle: str
    
    model_config = ConfigDict(from_attributes=True)
    
class SMaterials(SCreateMaterials):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    
class SMaterialsListSub(BaseModel):
    id: uuid.UUID
    title: str
    date_from: datetime
    date_to: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SMaterialsList(BaseModel):
    id: uuid.UUID
    title: str
    date_from: datetime
    date_to: datetime
    subcategories: list[SMaterialsListSub]
    
    model_config = ConfigDict(from_attributes=True)
    
class SMaterialsListDetail(BaseModel):
    id: uuid.UUID
    sender: str
    date: date
    request_number: str
    receiver: str
    item_name: str
    size: str
    quantity: str
    net_weight: str
    gross_weight: str
    volume: str
    carrier: str
    vehicle: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)