"""Manufacturing document flow card registry (mirrors frontend document-flow-cards.ts)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentFlowCardDef:
    id: str
    read_permissions: tuple[str, ...]


DOCUMENT_FLOW_CARDS: tuple[DocumentFlowCardDef, ...] = (
    DocumentFlowCardDef("customer-start", ("sales.customers.read",)),
    DocumentFlowCardDef("sales-order", ("sales.orders.read",)),
    DocumentFlowCardDef("mrp", ("manufacturing.planning.read",)),
    DocumentFlowCardDef("pr", ("procurement.records.read",)),
    DocumentFlowCardDef("po", ("warehouse.purchases.read",)),
    DocumentFlowCardDef("supplier", ("warehouse.suppliers.read",)),
    DocumentFlowCardDef("grn", ("procurement.records.read",)),
    DocumentFlowCardDef("raw-inv", ("warehouse.inventory.read",)),
    DocumentFlowCardDef("bom-wo", ("warehouse.bom.read", "manufacturing.ops.read")),
    DocumentFlowCardDef("mfg", ("manufacturing.ops.read",)),
    DocumentFlowCardDef("qc", ("manufacturing.quality.read",)),
    DocumentFlowCardDef("fg-inv", ("warehouse.inventory.read",)),
    DocumentFlowCardDef("fg-out", ("warehouse.inventory.read",)),
    DocumentFlowCardDef("do", ("sales.orders.read",)),
    DocumentFlowCardDef("invoice", ("finance.payments.read", "finance.records.read")),
    DocumentFlowCardDef("customer-end", ("sales.customers.read",)),
)

CARD_BY_ID: dict[str, DocumentFlowCardDef] = {c.id: c for c in DOCUMENT_FLOW_CARDS}


def user_can_read_card(user_codes: set[str], card: DocumentFlowCardDef) -> bool:
    return any(code in user_codes for code in card.read_permissions)
