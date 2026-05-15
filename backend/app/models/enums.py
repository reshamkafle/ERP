import enum


class ItemType(str, enum.Enum):
    RAW = "RAW"
    FINISHED = "FINISHED"
    TRADING = "TRADING"
    SERVICE = "SERVICE"
    ASSET = "ASSET"


class ItemLifecycleStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISCONTINUED = "DISCONTINUED"
    OBSOLETE = "OBSOLETE"


class ApprovalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
