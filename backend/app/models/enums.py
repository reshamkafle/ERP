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


class PurchaseStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    RECEIVED = "RECEIVED"


class ProcurementRunStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PromotionRunStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    DRAFT_REVIEW = "DRAFT_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
