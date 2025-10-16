import enum

from sqlalchemy import Enum


class RemarkActionEnum(str, enum.Enum):
    ACCEPT = "accept"
    DENY = "deny"
    
class ViolationActionEnum(str, enum.Enum):
    ACCEPT = "accept"
    DENY = "deny"

class ActObjectsActionEnum(str, enum.Enum):
    ACCEPT = "accept"
    DENY = "deny"
    
class ChecklistObjectsActionEnum(str, enum.Enum):
    ACCEPT = "accept"
    DENY = "deny"

class UserRoleEnum(str, enum.Enum):
    CONSTRUCTION_CONTROL = "construction_control"
    CONTRACTOR = "contractor"
    INSPECTIION = "inspection"
    
class ObjectStatusesEnum(str, enum.Enum):
    LEAD = "lead"
    DELAY = "delay"
    PLAN = "plan"
    KNOWN = "known"
    ACT = "act"
    
class ObjectTypeFilter(str, enum.Enum):
    ALL = "all"
    ACTIVE = "active"
    NOT_ACTIVE = "not_active"
    AGREEMENT = "agreement"
    ACT_OPENING = "act_opening"    
    
class ObjectTypeEnum(str, enum.Enum):
    ACTIVE = "active"
    NOT_ACTIVE = "not_active"
    AGREEMENT = "agreement"
    ACT_OPENING = "act_opening"
    
class DocumentStatusEnum(str, enum.Enum):
    YES = "yes"
    NO = "no"
    NOT_REQUIRED = "not_required"
    
class ActStatusEnum(str, enum.Enum):
    REQUIRED = "required"
    AWAITING = "awaiting"
    REJECTED = "rejected"
    ACCEPT = "accept"
    
class CheckListStatusEnum(str, enum.Enum):
    REQUIRED = "required"
    AWAITING = "awaiting"
    REJECTED = "rejected"
    ACCEPT = "accept"
    
class RemarksTypeFilter(str, enum.Enum):
    ALL = "all"
    ACTIVE = "active"
    CORRECTED = "corrected"
    REVIEW = "review"
    BLOCKERS = "blockers"    
    
class ViolationsTypeFilter(str, enum.Enum):
    ALL = "all"
    ACTIVE = "active"
    CORRECTED = "corrected"
    REVIEW = "review"
    BLOCKERS = "blockers" 
    
    
class RemarkStatusEnum(str, enum.Enum):
    FIXED = "fixed"
    NOT_FIXED = "not_fixed"
    REVIEW = "review"
    
class ViolationStatusEnum(str, enum.Enum):
    FIXED = "fixed"
    NOT_FIXED = "not_fixed"
    REVIEW = "review"
    

user_role_enum = Enum(UserRoleEnum, name="user_role_enum")
object_statuses_enum = Enum(ObjectStatusesEnum, name="object_statuses_enum")
object_type_enum = Enum(ObjectTypeEnum, name="object_type_enum")
document_status_enum = Enum(DocumentStatusEnum, name="document_status_enum")
act_status_enum = Enum(ActStatusEnum, name="act_status_enum")
check_list_status_enum = Enum(CheckListStatusEnum, name="check_list_status_enum")
remark_status_enum = Enum(RemarkStatusEnum, name="remark_status_enum")
violation_status_enum = Enum(ViolationStatusEnum, name="violation_status_enum")

