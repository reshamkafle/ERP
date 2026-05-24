"""Journey metadata for all ERP document types (order matches docs/ERP-DOCUMENT-JOURNEY.md)."""

from dataclasses import dataclass

from app.models.enums import ErpDocumentType


@dataclass(frozen=True)
class JourneyStepMeta:
    document_type: ErpDocumentType
    journey_step: int
    phase: str
    label: str
    slug: str
    number_prefix: str


JOURNEY_STEPS: tuple[JourneyStepMeta, ...] = (
    JourneyStepMeta(
        ErpDocumentType.TECH_PACK,
        1,
        "Product definition",
        "Tech Packs / Spec Sheets",
        "tech-packs-spec-sheets",
        "TECH",
    ),
    JourneyStepMeta(
        ErpDocumentType.BOM,
        2,
        "Product definition",
        "Bill of Materials (BOM)",
        "bill-of-materials",
        "BOM",
    ),
    JourneyStepMeta(
        ErpDocumentType.PURCHASE_ORDER,
        3,
        "Procurement",
        "Purchase Orders (POs)",
        "purchase-orders",
        "PO",
    ),
    JourneyStepMeta(
        ErpDocumentType.GRN,
        4,
        "Inbound & quality",
        "Goods Received Note (GRN)",
        "goods-received-note",
        "GRN",
    ),
    JourneyStepMeta(
        ErpDocumentType.INSPECTION_REPORT,
        5,
        "Inbound & quality",
        "Inspection Reports / Quality Certificates",
        "inspection-reports-quality-certificates",
        "INSP",
    ),
    JourneyStepMeta(
        ErpDocumentType.LAB_TEST_REPORT,
        6,
        "Inbound & quality",
        "Lab Test Reports / Compliance Certificates",
        "lab-test-reports-compliance",
        "LAB",
    ),
    JourneyStepMeta(
        ErpDocumentType.PRODUCTION_ORDER,
        7,
        "Production & internal stock",
        "Manufacturing / Production Orders / Work Orders / Cut Tickets",
        "manufacturing-production-orders",
        "MO",
    ),
    JourneyStepMeta(
        ErpDocumentType.STOCK_TRANSFER,
        8,
        "Production & internal stock",
        "Stock Transfer / Issue Slips",
        "stock-transfer-issue-slips",
        "STK",
    ),
    JourneyStepMeta(
        ErpDocumentType.INVENTORY_ADJUSTMENT,
        9,
        "Production & internal stock",
        "Inventory Adjustments / Cycle Count Reports",
        "inventory-adjustments-cycle-count",
        "ADJ",
    ),
    JourneyStepMeta(
        ErpDocumentType.PICK_LIST,
        10,
        "Fulfillment & outbound warehouse",
        "Pick Lists / Packing Slips",
        "pick-lists-packing-slips",
        "PICK",
    ),
    JourneyStepMeta(
        ErpDocumentType.PACKING_LIST,
        11,
        "Fulfillment & outbound warehouse",
        "Packing List",
        "packing-list",
        "PKL",
    ),
    JourneyStepMeta(
        ErpDocumentType.SHIPPING_MARKS,
        12,
        "Fulfillment & outbound warehouse",
        "Shipping Marks / Carton Labels",
        "shipping-marks-carton-labels",
        "LBL",
    ),
    JourneyStepMeta(
        ErpDocumentType.ASN,
        13,
        "Fulfillment & outbound warehouse",
        "Advance Shipping Notice (ASN)",
        "advance-shipping-notice",
        "ASN",
    ),
    JourneyStepMeta(
        ErpDocumentType.COMMERCIAL_INVOICE,
        14,
        "Export & trade finance",
        "Commercial Invoice",
        "commercial-invoice",
        "CI",
    ),
    JourneyStepMeta(
        ErpDocumentType.OUTGOING_INVOICE,
        15,
        "Export & trade finance",
        "Invoices (outgoing) and Debit/Credit Notes",
        "invoices-debit-credit-notes",
        "INV",
    ),
    JourneyStepMeta(
        ErpDocumentType.BILL_OF_LADING,
        16,
        "Export & trade finance",
        "Bill of Lading (BOL)",
        "bill-of-lading",
        "BOL",
    ),
    JourneyStepMeta(
        ErpDocumentType.CERTIFICATE_OF_ORIGIN,
        17,
        "Export & trade finance",
        "Certificate of Origin (COO)",
        "certificate-of-origin",
        "COO",
    ),
    JourneyStepMeta(
        ErpDocumentType.EXPORT_DECLARATION,
        18,
        "Export & trade finance",
        "Export Declaration / Shipping Bill",
        "export-declaration-shipping-bill",
        "EXP",
    ),
    JourneyStepMeta(
        ErpDocumentType.LETTER_OF_CREDIT,
        19,
        "Export & trade finance",
        "Letter of Credit (LC) documents",
        "letter-of-credit",
        "LC",
    ),
    JourneyStepMeta(
        ErpDocumentType.BILL_OF_EXCHANGE,
        20,
        "Export & trade finance",
        "Bill of Exchange",
        "bill-of-exchange",
        "BOE",
    ),
    JourneyStepMeta(
        ErpDocumentType.PROOF_OF_DELIVERY,
        21,
        "Delivery, settlement & costing",
        "Proof of Delivery (POD)",
        "proof-of-delivery",
        "POD",
    ),
    JourneyStepMeta(
        ErpDocumentType.PAYMENT_RECORD,
        22,
        "Delivery, settlement & costing",
        "Payment records (e.g., against LC or TT)",
        "payment-records",
        "PAY",
    ),
    JourneyStepMeta(
        ErpDocumentType.LANDED_COST,
        23,
        "Delivery, settlement & costing",
        "Cost sheets / Landed Cost calculations (including freight, duty)",
        "cost-sheets-landed-cost",
        "LCST",
    ),
)

JOURNEY_BY_TYPE: dict[ErpDocumentType, JourneyStepMeta] = {
    step.document_type: step for step in JOURNEY_STEPS
}
