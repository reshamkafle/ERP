from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from sqlalchemy import String, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.documents.journey import JOURNEY_BY_TYPE
from app.models.crm import CrmLead, CrmOpportunity, CustomerContact
from app.models.customer import Customer
from app.models.erp_document import ErpDocument
from app.models.manufacturing_ops import ProductionOrder
from app.models.module_record import ModuleRecord
from app.models.material_roll import MaterialRoll
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.sale import Sale, SaleItem
from app.models.supplier import Supplier
from app.models.warehouse import StorageLocation, Warehouse
from app.modules.catalog import MODULE_CATALOG
from app.schemas.search import SearchEntityType, SearchGroup, SearchHit, SearchRelatedHit

PER_TYPE_LIMIT = 8


@dataclass(frozen=True)
class EntityAccess:
    entity_type: SearchEntityType
    group: SearchGroup
    read_permissions: frozenset[str]


ENTITY_ACCESS: tuple[EntityAccess, ...] = (
    EntityAccess("customer", "sales", frozenset({"sales.customers.read"})),
    EntityAccess("sale", "sales", frozenset({"sales.orders.read", "sales.pos.use"})),
    EntityAccess("erp_document", "sales", frozenset({"warehouse.documents.read"})),
    EntityAccess("purchase", "procurement", frozenset({"warehouse.purchases.read"})),
    EntityAccess("supplier", "procurement", frozenset({"warehouse.suppliers.read"})),
    EntityAccess("production_order", "manufacturing", frozenset({"manufacturing.ops.read"})),
    EntityAccess("product", "inventory", frozenset({"warehouse.inventory.read"})),
    EntityAccess("material_roll", "inventory", frozenset({"warehouse.material_rolls.read"})),
    EntityAccess("warehouse", "inventory", frozenset({"warehouse.ops.read"})),
    EntityAccess("storage_location", "inventory", frozenset({"warehouse.ops.read"})),
    EntityAccess("module_record", "modules", frozenset()),  # per-module permission
    EntityAccess("crm_lead", "crm", frozenset({"crm.leads.read"})),
    EntityAccess("crm_opportunity", "crm", frozenset({"crm.opportunities.read"})),
    EntityAccess("crm_contact", "crm", frozenset({"crm.contacts.read"})),
)


def _has_any(permissions: set[str], codes: frozenset[str]) -> bool:
    return bool(codes) and any(code in permissions for code in codes)


def _pattern(query: str) -> str:
    # Escape SQL LIKE wildcards so user input cannot broaden matches unexpectedly.
    escaped = (
        query.strip()
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escaped}%"


def _can_access_entity(permissions: set[str], access: EntityAccess) -> bool:
    if access.entity_type == "module_record":
        return any(m.permission_read in permissions for m in MODULE_CATALOG)
    return _has_any(permissions, access.read_permissions)


def allowed_entity_types(
    permissions: set[str],
    requested: set[SearchEntityType] | None,
) -> set[SearchEntityType]:
    allowed = {
        access.entity_type
        for access in ENTITY_ACCESS
        if _can_access_entity(permissions, access)
    }
    if requested:
        allowed &= requested
    return allowed


def _allowed_module_codes(permissions: set[str]) -> list[str]:
    return [m.code for m in MODULE_CATALOG if m.permission_read in permissions]


def _erp_document_route(doc: ErpDocument, permissions: set[str]) -> str | None:
    if doc.sale_id is not None and _has_any(
        permissions,
        frozenset({"sales.orders.read", "sales.pos.use"}),
    ):
        return f"/sales/{doc.sale_id}"
    if doc.customer_id is not None and "sales.customers.read" in permissions:
        return f"/customers/{doc.customer_id}"
    if doc.purchase_id is not None and "warehouse.purchases.read" in permissions:
        return "/purchases"
    if doc.supplier_id is not None and "warehouse.suppliers.read" in permissions:
        return f"/suppliers/{doc.supplier_id}"
    return None


async def _related_docs_for_sale(
    db: AsyncSession,
    sale_id: int,
    permissions: set[str],
    limit: int = 3,
) -> list[SearchRelatedHit]:
    if "warehouse.documents.read" not in permissions:
        return []
    if not _has_any(permissions, frozenset({"sales.orders.read", "sales.pos.use"})):
        return []

    result = await db.execute(
        select(ErpDocument)
        .where(ErpDocument.sale_id == sale_id)
        .order_by(ErpDocument.journey_step)
        .limit(limit),
    )
    related: list[SearchRelatedHit] = []
    for doc in result.scalars().all():
        route = _erp_document_route(doc, permissions)
        if route is None:
            continue
        related.append(
            SearchRelatedHit(
                entity_type="erp_document",
                entity_id=doc.id,
                title=f"{doc.document_number} — {doc.title}",
                route=route,
            ),
        )
    return related


async def _search_customers(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    filter_expr = or_(
        Customer.name.ilike(pattern),
        Customer.customer_code.ilike(pattern),
        Customer.legal_name.ilike(pattern),
        Customer.trade_name.ilike(pattern),
        Customer.search_terms.ilike(pattern),
        Customer.phone.ilike(pattern),
        Customer.email.ilike(pattern),
        Customer.tax_id.ilike(pattern),
        Customer.gst_number.ilike(pattern),
        Customer.vat_number.ilike(pattern),
    )
    result = await db.execute(
        select(Customer).where(filter_expr).order_by(Customer.name).limit(limit),
    )
    hits: list[SearchHit] = []
    for c in result.scalars().all():
        hits.append(
            SearchHit(
                entity_type="customer",
                entity_id=c.id,
                title=c.name,
                subtitle=c.customer_code,
                route=f"/customers/{c.id}",
                group="sales",
                highlights=["name"],
            ),
        )
    return hits


async def _search_sales(
    db: AsyncSession,
    query: str,
    limit: int,
    permissions: set[str],
    *,
    sale_id: int | None = None,
) -> list[SearchHit]:
    pattern = _pattern(query)
    filters = [
        Sale.order_number.ilike(pattern),
        Sale.customer_po_number.ilike(pattern),
        Customer.name.ilike(pattern),
        Product.sku.ilike(pattern),
        Product.name.ilike(pattern),
        SaleItem.description.ilike(pattern),
    ]
    if query.strip().isdigit():
        filters.append(Sale.id == int(query.strip()))

    stmt = (
        select(Sale)
        .outerjoin(Customer, Sale.customer_id == Customer.id)
        .outerjoin(SaleItem, SaleItem.sale_id == Sale.id)
        .outerjoin(Product, SaleItem.product_id == Product.id)
        .where(or_(*filters))
        .options(selectinload(Sale.customer))
        .distinct()
        .order_by(Sale.created_at.desc())
        .limit(limit)
    )
    if sale_id is not None:
        stmt = stmt.where(Sale.id == sale_id)

    result = await db.execute(stmt)
    hits: list[SearchHit] = []
    for sale in result.scalars().unique().all():
        customer_name = sale.customer.name if sale.customer else None
        subtitle = sale.order_status.value
        if customer_name:
            subtitle = f"{customer_name} · {subtitle}"
        hits.append(
            SearchHit(
                entity_type="sale",
                entity_id=sale.id,
                title=sale.order_number,
                subtitle=subtitle,
                route=f"/sales/{sale.id}",
                group="sales",
                highlights=["order_number"],
                related=await _related_docs_for_sale(db, sale.id, permissions),
            ),
        )
    return hits


async def _search_erp_documents(
    db: AsyncSession,
    query: str,
    limit: int,
    permissions: set[str],
    *,
    sale_id: int | None = None,
) -> list[SearchHit]:
    pattern = _pattern(query)
    filter_expr = or_(
        ErpDocument.title.ilike(pattern),
        ErpDocument.document_number.ilike(pattern),
        ErpDocument.reference_number.ilike(pattern),
        ErpDocument.notes.ilike(pattern),
    )
    stmt = select(ErpDocument).where(filter_expr).order_by(ErpDocument.created_at.desc()).limit(limit * 2)
    if sale_id is not None:
        stmt = stmt.where(ErpDocument.sale_id == sale_id)

    result = await db.execute(stmt)
    hits: list[SearchHit] = []
    for doc in result.scalars().all():
        route = _erp_document_route(doc, permissions)
        if route is None:
            continue
        meta = JOURNEY_BY_TYPE[doc.document_type]
        hits.append(
            SearchHit(
                entity_type="erp_document",
                entity_id=doc.id,
                title=f"{doc.document_number} — {doc.title}",
                subtitle=f"{meta.label} · {doc.status.value}",
                route=route,
                group="sales" if doc.sale_id else "modules",
                highlights=["document_number"],
            ),
        )
        if len(hits) >= limit:
            break
    return hits


async def _search_purchases(
    db: AsyncSession,
    query: str,
    limit: int,
    permissions: set[str],
) -> list[SearchHit]:
    pattern = _pattern(query)
    filters = [cast(Purchase.id, String).ilike(pattern)]
    if "warehouse.suppliers.read" in permissions:
        filters.append(Supplier.name.ilike(pattern))

    stmt = (
        select(Purchase)
        .outerjoin(Supplier, Purchase.supplier_id == Supplier.id)
        .options(selectinload(Purchase.supplier))
        .where(or_(*filters))
        .order_by(Purchase.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    hits: list[SearchHit] = []
    for purchase in result.scalars().unique().all():
        subtitle = purchase.status.value
        if "warehouse.suppliers.read" in permissions and purchase.supplier:
            subtitle = f"{purchase.supplier.name} · {subtitle}"
        hits.append(
            SearchHit(
                entity_type="purchase",
                entity_id=purchase.id,
                title=f"PO #{purchase.id}",
                subtitle=subtitle,
                route="/purchases",
                group="procurement",
                highlights=["id"],
            ),
        )
    return hits


async def _search_production_orders(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    stmt = (
        select(ProductionOrder)
        .outerjoin(Product, ProductionOrder.product_id == Product.id)
        .options(selectinload(ProductionOrder.product))
        .where(
            or_(
                ProductionOrder.order_number.ilike(pattern),
                Product.sku.ilike(pattern),
                Product.name.ilike(pattern),
            ),
        )
        .order_by(ProductionOrder.id.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    hits: list[SearchHit] = []
    for po in result.scalars().unique().all():
        product_name = po.product.name if po.product else None
        hits.append(
            SearchHit(
                entity_type="production_order",
                entity_id=po.id,
                title=po.order_number,
                subtitle=f"{product_name or '—'} · {po.status.value}",
                route="/manufacturing?feature=production_orders",
                group="manufacturing",
                highlights=["order_number"],
            ),
        )
    return hits


async def _search_suppliers(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    filter_expr = or_(
        Supplier.name.ilike(pattern),
        Supplier.vendor_code.ilike(pattern),
        Supplier.legal_name.ilike(pattern),
        Supplier.phone.ilike(pattern),
        Supplier.email.ilike(pattern),
        Supplier.vendor_category.ilike(pattern),
    )
    result = await db.execute(
        select(Supplier).where(filter_expr).order_by(Supplier.name).limit(limit),
    )
    hits: list[SearchHit] = []
    for s in result.scalars().all():
        hits.append(
            SearchHit(
                entity_type="supplier",
                entity_id=s.id,
                title=s.name,
                subtitle=s.vendor_code,
                route=f"/suppliers/{s.id}",
                group="procurement",
                highlights=["name"],
            ),
        )
    return hits


async def _search_products(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    filter_expr = or_(
        Product.sku.ilike(pattern),
        Product.name.ilike(pattern),
        Product.barcode.ilike(pattern),
        Product.alternate_codes.ilike(pattern),
        Product.style_code.ilike(pattern),
        Product.color.ilike(pattern),
        Product.size.ilike(pattern),
        Product.variant.ilike(pattern),
    )
    result = await db.execute(
        select(Product).where(filter_expr).order_by(Product.name).limit(limit),
    )
    hits: list[SearchHit] = []
    for p in result.scalars().all():
        item_type = p.item_type.value if p.item_type else None
        route = "/inventory"
        if item_type == "RAW":
            route = "/inventory?item_type=RAW"
        elif item_type == "FINISHED":
            route = "/inventory?item_type=FINISHED"
        hits.append(
            SearchHit(
                entity_type="product",
                entity_id=p.id,
                title=f"{p.sku} — {p.name}",
                subtitle=item_type,
                route=route,
                group="inventory",
                highlights=["sku"],
            ),
        )
    return hits


async def _search_material_rolls(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    filter_expr = or_(
        MaterialRoll.roll_number.ilike(pattern),
        MaterialRoll.barcode.ilike(pattern),
        MaterialRoll.rfid_tag.ilike(pattern),
        MaterialRoll.dye_lot.ilike(pattern),
        MaterialRoll.supplier_lot_number.ilike(pattern),
    )
    result = await db.execute(
        select(MaterialRoll)
        .where(filter_expr)
        .order_by(MaterialRoll.updated_at.desc())
        .limit(limit),
    )
    hits: list[SearchHit] = []
    for roll in result.scalars().all():
        hits.append(
            SearchHit(
                entity_type="material_roll",
                entity_id=roll.id,
                title=roll.roll_number,
                subtitle=f"{roll.remaining_quantity} {roll.primary_uom}",
                route=f"/inventory/fabric-rolls?roll={roll.id}",
                group="inventory",
                highlights=["roll_number"],
            ),
        )
    return hits


async def _search_warehouses(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    filter_expr = or_(
        Warehouse.code.ilike(pattern),
        Warehouse.name.ilike(pattern),
    )
    result = await db.execute(
        select(Warehouse).where(filter_expr).order_by(Warehouse.code).limit(limit),
    )
    hits: list[SearchHit] = []
    for wh in result.scalars().all():
        hits.append(
            SearchHit(
                entity_type="warehouse",
                entity_id=wh.id,
                title=f"{wh.code} — {wh.name}",
                subtitle=wh.warehouse_type.value,
                route=f"/warehouses?search={quote(wh.code)}",
                group="inventory",
                highlights=["code"],
            ),
        )
    return hits


async def _search_storage_locations(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    filter_expr = or_(
        StorageLocation.code.ilike(pattern),
        StorageLocation.zone.ilike(pattern),
        StorageLocation.aisle.ilike(pattern),
        StorageLocation.row.ilike(pattern),
        StorageLocation.column.ilike(pattern),
        StorageLocation.level.ilike(pattern),
    )
    stmt = (
        select(StorageLocation)
        .join(Warehouse, StorageLocation.warehouse_id == Warehouse.id)
        .options(selectinload(StorageLocation.warehouse))
        .where(filter_expr)
        .order_by(StorageLocation.code)
        .limit(limit)
    )
    result = await db.execute(stmt)
    hits: list[SearchHit] = []
    for loc in result.scalars().unique().all():
        warehouse_name = loc.warehouse.name if loc.warehouse else None
        hits.append(
            SearchHit(
                entity_type="storage_location",
                entity_id=loc.id,
                title=loc.code,
                subtitle=warehouse_name,
                route=(
                    f"/locations?search={quote(loc.code)}"
                    f"&warehouse_id={loc.warehouse_id}"
                ),
                group="inventory",
                highlights=["code"],
            ),
        )
    return hits


async def _search_module_records(
    db: AsyncSession,
    query: str,
    limit: int,
    permissions: set[str],
) -> list[SearchHit]:
    module_codes = _allowed_module_codes(permissions)
    if not module_codes:
        return []

    pattern = _pattern(query)
    per_module = max(1, limit // max(len(module_codes), 1))
    hits: list[SearchHit] = []

    for module_code in module_codes:
        module_def = next(m for m in MODULE_CATALOG if m.code == module_code)
        expr = or_(
            ModuleRecord.title.ilike(pattern),
            ModuleRecord.reference.ilike(pattern),
            ModuleRecord.party_name.ilike(pattern),
            ModuleRecord.description.ilike(pattern),
            cast(ModuleRecord.extra_data, String).ilike(pattern),
        )
        result = await db.execute(
            select(ModuleRecord)
            .where(ModuleRecord.module_code == module_code)
            .where(expr)
            .order_by(ModuleRecord.updated_at.desc())
            .limit(per_module),
        )
        for record in result.scalars().all():
            route = f"{module_def.route_path}?feature={record.feature_code}"
            hits.append(
                SearchHit(
                    entity_type="module_record",
                    entity_id=record.id,
                    title=record.title,
                    subtitle=f"{module_def.short_name} · {record.reference}",
                    route=route,
                    group="modules",
                    highlights=["title"],
                ),
            )
    return hits[:limit]


async def _search_crm_leads(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    result = await db.execute(
        select(CrmLead)
        .where(
            or_(
                CrmLead.company_name.ilike(pattern),
                CrmLead.contact_name.ilike(pattern),
                CrmLead.email.ilike(pattern),
            ),
        )
        .order_by(CrmLead.updated_at.desc())
        .limit(limit),
    )
    return [
        SearchHit(
            entity_type="crm_lead",
            entity_id=lead.id,
            title=lead.company_name,
            subtitle=lead.contact_name,
            route="/crm",
            group="crm",
            highlights=["company_name"],
        )
        for lead in result.scalars().all()
    ]


async def _search_crm_opportunities(db: AsyncSession, query: str, limit: int) -> list[SearchHit]:
    pattern = _pattern(query)
    result = await db.execute(
        select(CrmOpportunity)
        .where(
            or_(
                CrmOpportunity.title.ilike(pattern),
            ),
        )
        .order_by(CrmOpportunity.updated_at.desc())
        .limit(limit),
    )
    return [
        SearchHit(
            entity_type="crm_opportunity",
            entity_id=opp.id,
            title=opp.title,
            subtitle=opp.stage.value if opp.stage else None,
            route="/crm",
            group="crm",
            highlights=["title"],
        )
        for opp in result.scalars().all()
    ]


async def _search_crm_contacts(
    db: AsyncSession,
    query: str,
    limit: int,
    permissions: set[str],
) -> list[SearchHit]:
    pattern = _pattern(query)
    result = await db.execute(
        select(CustomerContact)
        .where(
            or_(
                CustomerContact.name.ilike(pattern),
                CustomerContact.first_name.ilike(pattern),
                CustomerContact.last_name.ilike(pattern),
                CustomerContact.email.ilike(pattern),
            ),
        )
        .order_by(CustomerContact.name)
        .limit(limit * 2),
    )
    hits: list[SearchHit] = []
    for contact in result.scalars().all():
        if "sales.customers.read" in permissions:
            route = f"/customers/{contact.customer_id}"
        else:
            route = "/crm"
        hits.append(
            SearchHit(
                entity_type="crm_contact",
                entity_id=contact.id,
                title=contact.name,
                subtitle=contact.role,
                route=route,
                group="crm",
                highlights=["name"],
            ),
        )
        if len(hits) >= limit:
            break
    return hits


async def unified_search(
    db: AsyncSession,
    *,
    query: str,
    permissions: set[str],
    types: set[SearchEntityType] | None = None,
    limit: int = 20,
    sale_id: int | None = None,
) -> list[SearchHit]:
    q = query.strip()
    if len(q) < 2:
        return []

    allowed = allowed_entity_types(permissions, types)
    per_type = min(PER_TYPE_LIMIT, limit)
    hits: list[SearchHit] = []

    if sale_id is not None:
        if not _has_any(permissions, frozenset({"sales.orders.read", "sales.pos.use"})):
            return []
        if "sale" in allowed:
            hits.extend(await _search_sales(db, q, 1, permissions, sale_id=sale_id))
        if "erp_document" in allowed:
            hits.extend(
                await _search_erp_documents(db, q, per_type, permissions, sale_id=sale_id),
            )
        return hits[:limit]

    if "customer" in allowed:
        hits.extend(await _search_customers(db, q, per_type))
    if "sale" in allowed:
        hits.extend(await _search_sales(db, q, per_type, permissions))
    if "erp_document" in allowed:
        hits.extend(await _search_erp_documents(db, q, per_type, permissions))
    if "purchase" in allowed:
        hits.extend(await _search_purchases(db, q, per_type, permissions))
    if "production_order" in allowed:
        hits.extend(await _search_production_orders(db, q, per_type))
    if "supplier" in allowed:
        hits.extend(await _search_suppliers(db, q, per_type))
    if "product" in allowed:
        hits.extend(await _search_products(db, q, per_type))
    if "material_roll" in allowed:
        hits.extend(await _search_material_rolls(db, q, per_type))
    if "warehouse" in allowed:
        hits.extend(await _search_warehouses(db, q, per_type))
    if "storage_location" in allowed:
        hits.extend(await _search_storage_locations(db, q, per_type))
    if "module_record" in allowed:
        hits.extend(await _search_module_records(db, q, per_type, permissions))
    if "crm_lead" in allowed:
        hits.extend(await _search_crm_leads(db, q, per_type))
    if "crm_opportunity" in allowed:
        hits.extend(await _search_crm_opportunities(db, q, per_type))
    if "crm_contact" in allowed:
        hits.extend(await _search_crm_contacts(db, q, per_type, permissions))

    return hits[:limit]
