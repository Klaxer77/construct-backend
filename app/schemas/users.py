import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRoleEnum
from app.schemas.company import SCompanyCurrent


class SUsersContractor(BaseModel):
    id: uuid.UUID
    using_id: int
    avatar: str | None
    email: str
    fio: str
    role: UserRoleEnum
    company: SCompanyCurrent
    
    model_config = ConfigDict(from_attributes=True)

class SUserRole(BaseModel):
    role: UserRoleEnum
    
class SUserObjectAccess(BaseModel):
    object_id: uuid.UUID
    is_active: bool
    access_expires_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)
    
class SUserCurrentSubObject(BaseModel):
    id: uuid.UUID
    using_id: int
    avatar: str | None
    email: str
    fio: str
    role: UserRoleEnum

class SUserCurrent(BaseModel):
    id: uuid.UUID
    using_id: int
    avatar: str | None
    email: str
    fio: str
    role: UserRoleEnum
    object_access: list[SUserObjectAccess]
    
    model_config = ConfigDict(from_attributes=True)


class SUserLogin(BaseModel):
    email: EmailStr
    password: str

class SUserLogout(BaseModel):
    result: str

class SUserTokens(BaseModel):
    access_token: str
    refresh_token: uuid.UUID