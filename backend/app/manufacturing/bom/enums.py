import enum


class ItemCategory(str, enum.Enum):
    FABRIC = "FABRIC"
    TRIM = "TRIM"
    ACCESSORY = "ACCESSORY"
    SUB_ASSEMBLY = "SUB_ASSEMBLY"
    FINISHED_GOOD = "FINISHED_GOOD"


class ConsumptionType(str, enum.Enum):
    FABRIC = "FABRIC"
    TRIM = "TRIM"
    OTHER = "OTHER"


class UnitOfMeasure(str, enum.Enum):
    METER = "meter"
    KG = "kg"
    PIECE = "piece"
    YARD = "yard"
    GRAM = "gram"
    SET = "set"
    EA = "ea"


class BOMStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    OBSOLETE = "OBSOLETE"
    SUPERSEDED = "SUPERSEDED"


class BOMType(str, enum.Enum):
    MANUFACTURING = "MANUFACTURING"
    ENGINEERING = "ENGINEERING"
    SALES = "SALES"
    SERVICE = "SERVICE"
    PHANTOM = "PHANTOM"
