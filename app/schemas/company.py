import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ObjectStatusesEnum


class SCompanyCurrent(BaseModel):
    id: uuid.UUID
    title: str
    
    model_config = ConfigDict(from_attributes=True)

class ResponsibleUserSub(BaseModel):
    fio: str
    
    model_config = ConfigDict(from_attributes=True)

class SCompanyProjectStatuses(BaseModel):
    id: uuid.UUID
    title: str
    city: str
    updated_at: datetime
    status: ObjectStatusesEnum
    responsible_user: ResponsibleUserSub | None
    coords: list[tuple[float, float]] | list[list[tuple[float, float]]]
    
    model_config = ConfigDict(from_attributes=True)