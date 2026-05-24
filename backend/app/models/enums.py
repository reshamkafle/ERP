import enum


class ItemType(str, enum.Enum):
    RAW = "RAW"
    FINISHED = "FINISHED"
    SEMI_FINISHED = "SEMI_FINISHED"
    CONSUMABLE = "CONSUMABLE"
    TRADING = "TRADING"
    SERVICE = "SERVICE"
    ASSET = "ASSET"


class AbcClass(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class XyzClass(str, enum.Enum):
    FAST = "FAST"
    SLOW = "SLOW"
    NON_MOVING = "NON_MOVING"


class CostValuationMethod(str, enum.Enum):
    STANDARD = "STANDARD"
    AVERAGE = "AVERAGE"
    LAST_PURCHASE = "LAST_PURCHASE"
    FIFO = "FIFO"
    LIFO = "LIFO"


class WarehouseType(str, enum.Enum):
    MAIN = "MAIN"
    DISTRIBUTION = "DISTRIBUTION"
    PRODUCTION = "PRODUCTION"
    COLD_STORAGE = "COLD_STORAGE"
    THIRD_PARTY = "THIRD_PARTY"
    OTHER = "OTHER"


class WarehouseStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class StorageLocationType(str, enum.Enum):
    BULK = "BULK"
    PICKING = "PICKING"
    RECEIVING = "RECEIVING"
    SHIPPING = "SHIPPING"
    QUARANTINE = "QUARANTINE"
    STAGING = "STAGING"
    WIP = "WIP"
    OTHER = "OTHER"


class StorageLocationStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BLOCKED = "BLOCKED"
    DAMAGED = "DAMAGED"


class StockQualityStatus(str, enum.Enum):
    QUARANTINE = "QUARANTINE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class InventoryTransactionType(str, enum.Enum):
    RECEIPT = "RECEIPT"
    ISSUE = "ISSUE"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"
    WRITE_OFF = "WRITE_OFF"
    CYCLE_COUNT = "CYCLE_COUNT"
    PRODUCTION_ISSUE = "PRODUCTION_ISSUE"
    PRODUCTION_RECEIPT = "PRODUCTION_RECEIPT"
    WIP_TRANSFER = "WIP_TRANSFER"


class MaterialRollStatus(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    ALLOCATED = "ALLOCATED"
    IN_PRODUCTION = "IN_PRODUCTION"
    ON_HOLD = "ON_HOLD"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"
    SHIPPED = "SHIPPED"


class MaterialFinishType(str, enum.Enum):
    GREIGE = "GREIGE"
    DYED = "DYED"
    PRINTED = "PRINTED"
    FINISHED = "FINISHED"
    OTHER = "OTHER"


class MaterialRollMovementType(str, enum.Enum):
    RECEIPT = "RECEIPT"
    TRANSFER = "TRANSFER"
    ISSUE = "ISSUE"
    RETURN = "RETURN"
    ADJUSTMENT = "ADJUSTMENT"
    ALLOCATE = "ALLOCATE"
    DEALLOCATE = "DEALLOCATE"
    SHIP = "SHIP"
    QUARANTINE = "QUARANTINE"
    CYCLE_COUNT = "CYCLE_COUNT"


class MaterialRollAllocationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    RELEASED = "RELEASED"


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


class ErpDocumentType(str, enum.Enum):
    TECH_PACK = "TECH_PACK"
    BOM = "BOM"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    GRN = "GRN"
    INSPECTION_REPORT = "INSPECTION_REPORT"
    LAB_TEST_REPORT = "LAB_TEST_REPORT"
    CERTIFICATE_OF_ANALYSIS = "CERTIFICATE_OF_ANALYSIS"
    PRODUCTION_ORDER = "PRODUCTION_ORDER"
    STOCK_TRANSFER = "STOCK_TRANSFER"
    INVENTORY_ADJUSTMENT = "INVENTORY_ADJUSTMENT"
    PICK_LIST = "PICK_LIST"
    PACKING_LIST = "PACKING_LIST"
    SHIPPING_MARKS = "SHIPPING_MARKS"
    ASN = "ASN"
    COMMERCIAL_INVOICE = "COMMERCIAL_INVOICE"
    OUTGOING_INVOICE = "OUTGOING_INVOICE"
    BILL_OF_LADING = "BILL_OF_LADING"
    CERTIFICATE_OF_ORIGIN = "CERTIFICATE_OF_ORIGIN"
    EXPORT_DECLARATION = "EXPORT_DECLARATION"
    LETTER_OF_CREDIT = "LETTER_OF_CREDIT"
    BILL_OF_EXCHANGE = "BILL_OF_EXCHANGE"
    PROOF_OF_DELIVERY = "PROOF_OF_DELIVERY"
    PAYMENT_RECORD = "PAYMENT_RECORD"
    LANDED_COST = "LANDED_COST"


class ErpDocumentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class TaxType(str, enum.Enum):
    VAT = "VAT"
    GST = "GST"
    SALES_TAX = "SALES_TAX"
    WITHHOLDING = "WITHHOLDING"
    OTHER = "OTHER"


class DocumentPaymentStatus(str, enum.Enum):
    UNPAID = "UNPAID"
    PARTIAL = "PARTIAL"
    PAID = "PAID"


class PaymentDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class PaymentType(str, enum.Enum):
    CUSTOMER_RECEIPT = "CUSTOMER_RECEIPT"
    SUPPLIER_PAYMENT = "SUPPLIER_PAYMENT"
    PAYROLL = "PAYROLL"
    EXPENSE = "EXPENSE"
    OTHER = "OTHER"


class PaymentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class PartyType(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    SUPPLIER = "SUPPLIER"
    EMPLOYEE = "EMPLOYEE"


class AllocationType(str, enum.Enum):
    INVOICE = "INVOICE"
    DISCOUNT = "DISCOUNT"
    OVERPAYMENT = "OVERPAYMENT"
    WRITE_OFF = "WRITE_OFF"


class AccountType(str, enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class JournalEntryStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    REVERSED = "REVERSED"


class JournalSourceType(str, enum.Enum):
    PAYMENT = "PAYMENT"
    SALE = "SALE"
    PURCHASE = "PURCHASE"
    MANUAL = "MANUAL"
    MANUFACTURING = "MANUFACTURING"


class SaleOrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CREATED = "CREATED"
    RELEASED = "RELEASED"
    IN_PROCESS = "IN_PROCESS"
    DELIVERED = "DELIVERED"
    INVOICED = "INVOICED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class SaleOrderType(str, enum.Enum):
    STANDARD = "STANDARD"
    RUSH = "RUSH"
    SAMPLE = "SAMPLE"
    RETURN = "RETURN"
    EXPORT = "EXPORT"


class SaleChannel(str, enum.Enum):
    DIRECT = "DIRECT"
    DISTRIBUTOR = "DISTRIBUTOR"
    ECOMMERCE = "ECOMMERCE"
    RETAIL = "RETAIL"


class SaleOrderSource(str, enum.Enum):
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    PORTAL = "PORTAL"
    WEBSITE = "WEBSITE"
    EDI = "EDI"
    MOBILE = "MOBILE"


class OrderPriority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SaleLineStatus(str, enum.Enum):
    OPEN = "OPEN"
    ALLOCATED = "ALLOCATED"
    PARTIAL = "PARTIAL"
    DELIVERED = "DELIVERED"
    INVOICED = "INVOICED"
    CANCELLED = "CANCELLED"


class CreditCheckStatus(str, enum.Enum):
    NOT_RUN = "NOT_RUN"
    PASSED = "PASSED"
    FAILED = "FAILED"
    OVERRIDE = "OVERRIDE"


class AtpCheckStatus(str, enum.Enum):
    NOT_RUN = "NOT_RUN"
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"


class DeliveryStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class BillingStatus(str, enum.Enum):
    NOT_INVOICED = "NOT_INVOICED"
    PARTIAL = "PARTIAL"
    INVOICED = "INVOICED"
    COMPLETE = "COMPLETE"


class SalePartnerRole(str, enum.Enum):
    SOLD_TO = "SOLD_TO"
    SHIP_TO = "SHIP_TO"
    BILL_TO = "BILL_TO"
    PAYER = "PAYER"
    FORWARDING_AGENT = "FORWARDING_AGENT"
    SALES_EMPLOYEE = "SALES_EMPLOYEE"


class SaleItemCategory(str, enum.Enum):
    STANDARD = "STANDARD"
    FREE_GOODS = "FREE_GOODS"
    SAMPLE = "SAMPLE"
    RETURN = "RETURN"
    SERVICE = "SERVICE"


class CustomerSegment(str, enum.Enum):
    VIP = "VIP"
    REGULAR = "REGULAR"
    NEW = "NEW"
    PROSPECT = "PROSPECT"
    INACTIVE = "INACTIVE"


class CustomerStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PROSPECT = "PROSPECT"
    BLOCKED = "BLOCKED"


class CustomerType(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"
    GOVERNMENT = "GOVERNMENT"
    DISTRIBUTOR = "DISTRIBUTOR"
    RETAIL = "RETAIL"
    OTHER = "OTHER"


class CustomerAddressType(str, enum.Enum):
    PRIMARY = "PRIMARY"
    BILLING = "BILLING"
    SHIPPING = "SHIPPING"
    HEAD_OFFICE = "HEAD_OFFICE"
    BRANCH = "BRANCH"
    FACTORY = "FACTORY"
    OTHER = "OTHER"


class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class OpportunityStage(str, enum.Enum):
    PROSPECTING = "PROSPECTING"
    QUALIFICATION = "QUALIFICATION"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class CrmActivityType(str, enum.Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    NOTE = "NOTE"
    VISIT = "VISIT"
    TASK = "TASK"
    DEMO = "DEMO"
    SITE_VISIT = "SITE_VISIT"


class CommunicationChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SMS = "SMS"
    IN_PERSON = "IN_PERSON"
    PORTAL = "PORTAL"


class InfluenceLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    DECISION_MAKER = "DECISION_MAKER"


class ProductionOrderStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    RELEASED = "RELEASED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class ProductionOrderSource(str, enum.Enum):
    MANUAL = "MANUAL"
    MRP = "MRP"
    SALES = "SALES"


class MaterialIssueMethod(str, enum.Enum):
    MANUAL = "MANUAL"
    BACKFLUSH = "BACKFLUSH"


class MrpRunStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PlannedOrderType(str, enum.Enum):
    MAKE = "MAKE"
    BUY = "BUY"


class InspectionStage(str, enum.Enum):
    INBOUND = "INBOUND"
    IN_PROCESS = "IN_PROCESS"
    FINAL = "FINAL"


class NonConformanceDisposition(str, enum.Enum):
    SCRAP = "SCRAP"
    REWORK = "REWORK"
    RETURN = "RETURN"
    USE_AS_IS = "USE_AS_IS"


class EngineeringChangeStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    IMPLEMENTED = "IMPLEMENTED"


class VarianceType(str, enum.Enum):
    MATERIAL = "MATERIAL"
    LABOR = "LABOR"
    OVERHEAD = "OVERHEAD"


class ProductionContractType(str, enum.Enum):
    CMT = "CMT"
    FOB = "FOB"


class ProductionPhase(str, enum.Enum):
    CUT = "CUT"
    MAKE = "MAKE"
    TRIM = "TRIM"


class ProductionPlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class CutOrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    RELEASED = "RELEASED"
    CUTTING = "CUTTING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
