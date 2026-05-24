#!/usr/bin/env python3
"""RBAC negative authorization probe using 50 seed users against a running API."""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import sys
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import func, select, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.bootstrap import seed_admin_user  # noqa: E402
from app.core.database import AsyncSessionLocal, init_db  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.core.seed_rbac_users_manifest import SEED_USERS, SeedUserSpec  # noqa: E402
from app.crud import sale as sale_crud  # noqa: E402
from app.crud import erp_document as erp_document_crud  # noqa: E402
from app.models.customer import Customer  # noqa: E402
from app.models.enums import ErpDocumentStatus, ErpDocumentType, ItemLifecycleStatus  # noqa: E402
from app.models.payment import Payment  # noqa: E402
from app.models.payment_method import PaymentMethod  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.models.purchase import Purchase  # noqa: E402
from app.models.role import Role  # noqa: E402
from app.models.sale import Sale  # noqa: E402
from app.models.supplier import Supplier  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.schemas.erp_document import ErpDocumentCreate  # noqa: E402
from app.schemas.payments import ReceivePaymentCreate  # noqa: E402
from app.schemas.sale import SaleItemLineCreate, SaleOrderCreate  # noqa: E402
from app.services import payment_service  # noqa: E402
from app.testing.seed_agent_demo import seed_agent_demo_data  # noqa: E402

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_PASSWORD = os.environ.get("SEED_USER_PASSWORD", "SeedUser123!")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "seed-output" / "rbac-breach-report.md"
SUPER_ADMIN_EMAIL = "rbac-01-super-admin-a@seed.local"


@dataclass
class FixtureIds:
    sale_id: int | None = None
    product_id: int | None = None
    product_sku: str | None = None
    customer_id: int | None = None
    supplier_id: int | None = None
    purchase_id: int | None = None
    document_id: int | None = None
    payment_id: int | None = None
    payment_method_id: int | None = None
    role_id: int | None = None
    lead_id: int | None = None


@dataclass(frozen=True)
class ProbeSpec:
    key: str
    method: str
    path: str
    required_permissions: tuple[str, ...]
    body: Callable[[FixtureIds], dict[str, Any] | None]
    fixture_fields: tuple[str, ...] = ()


def _has_any_permission(user_perms: set[str], required: tuple[str, ...]) -> bool:
    return any(code in user_perms for code in required)


def _missing_fixtures(fixtures: FixtureIds, fields: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for name in fields:
        if getattr(fixtures, name) is None:
            missing.append(name)
    return missing


def _build_probes() -> tuple[ProbeSpec, ...]:
    today = date.today().isoformat()
    uid = uuid.uuid4().hex[:8]

    def sales_patch_body(f: FixtureIds) -> dict[str, Any] | None:
        return {"header_text": f"rbac-probe-{uid}"}

    def sales_create_body(f: FixtureIds) -> dict[str, Any] | None:
        if f.product_id is None:
            return None
        return {
            "items": [{"product_id": f.product_id, "quantity": 1}],
            "confirm": False,
        }

    def sales_confirm_body(f: FixtureIds) -> dict[str, Any] | None:
        return {"run_credit_check": False, "run_atp_check": False}

    def pos_checkout_body(f: FixtureIds) -> dict[str, Any] | None:
        if f.product_id is None:
            return None
        return {
            "items": [{"product_id": f.product_id, "quantity": 1}],
            "confirm": False,
        }

    def purchase_create_body(f: FixtureIds) -> dict[str, Any] | None:
        if f.supplier_id is None or f.product_id is None:
            return None
        return {
            "supplier_id": f.supplier_id,
            "items": [{"product_id": f.product_id, "quantity": 1}],
        }

    def inventory_patch_body(f: FixtureIds) -> dict[str, Any] | None:
        return {"description": f"rbac-probe-{uid}"}

    def customer_patch_body(f: FixtureIds) -> dict[str, Any] | None:
        return {"search_terms": f"rbac-probe-{uid}"}

    def supplier_create_body(f: FixtureIds) -> dict[str, Any] | None:
        return {
            "vendor_code": f"RBAC{uid.upper()[:8]}",
            "name": f"RBAC Probe Vendor {uid}",
        }

    def document_create_body(f: FixtureIds) -> dict[str, Any] | None:
        return {
            "document_type": "TECH_PACK",
            "title": f"RBAC probe {uid}",
            "status": "DRAFT",
        }

    def bom_write_body(f: FixtureIds) -> dict[str, Any] | None:
        return {"lines": []}

    def material_roll_body(f: FixtureIds) -> dict[str, Any] | None:
        if f.product_id is None:
            return None
        return {
            "product_id": f.product_id,
            "initial_quantity": "1",
            "primary_uom": "meter",
        }

    def crm_lead_body(f: FixtureIds) -> dict[str, Any] | None:
        return {"company_name": f"RBAC Probe Co {uid}"}

    def crm_opp_body(f: FixtureIds) -> dict[str, Any] | None:
        if f.customer_id is None:
            return None
        return {
            "customer_id": f.customer_id,
            "title": f"RBAC Opp {uid}",
        }

    def tax_create_body(f: FixtureIds) -> dict[str, Any] | None:
        return {
            "code": f"RBAC{uid.upper()[:10]}",
            "name": f"RBAC Tax {uid}",
            "rate_percent": "5.00",
            "tax_type": "OTHER",
            "country_code": "US",
            "effective_from": today,
            "is_active": True,
        }

    def payment_receive_body(f: FixtureIds) -> dict[str, Any] | None:
        if f.customer_id is None or f.payment_method_id is None:
            return None
        return {
            "customer_id": f.customer_id,
            "payment_method_id": f.payment_method_id,
            "amount": "1.00",
            "payment_date": today,
        }

    def promotion_body(_: FixtureIds) -> dict[str, Any]:
        return {}

    def procurement_body(_: FixtureIds) -> dict[str, Any]:
        return {}

    def mfg_po_body(f: FixtureIds) -> dict[str, Any] | None:
        if f.product_id is None:
            return None
        return {"product_id": f.product_id, "quantity_planned": "1"}

    def mfg_plan_body(_: FixtureIds) -> dict[str, Any]:
        return {"notes": f"rbac-probe-{uid}"}

    def mfg_wc_body(_: FixtureIds) -> dict[str, Any]:
        return {
            "code": f"RB{uid[:6].upper()}",
            "name": f"RBAC WC {uid}",
        }

    def access_roles_body(_: FixtureIds) -> dict[str, Any]:
        return {"permission_codes": []}

    def layout_body(_: FixtureIds) -> dict[str, Any]:
        return {"layout": {"theme": "light", "sidebar_collapsed": False, "hidden_nav_slugs": []}}

    return (
        ProbeSpec(
            "sales_patch",
            "PATCH",
            "/api/v1/sales/{sale_id}",
            ("sales.orders.write",),
            sales_patch_body,
            ("sale_id",),
        ),
        ProbeSpec(
            "sales_create",
            "POST",
            "/api/v1/sales",
            ("sales.orders.write",),
            sales_create_body,
            ("product_id",),
        ),
        ProbeSpec(
            "sales_confirm",
            "POST",
            "/api/v1/sales/{sale_id}/confirm",
            ("sales.orders.write",),
            sales_confirm_body,
            ("sale_id",),
        ),
        ProbeSpec(
            "pos_checkout",
            "POST",
            "/api/v1/sales/checkout",
            ("sales.pos.use",),
            pos_checkout_body,
            ("product_id",),
        ),
        ProbeSpec(
            "promotions_run",
            "POST",
            "/api/v1/promotion-runs",
            ("sales.promotions.manage",),
            promotion_body,
        ),
        ProbeSpec(
            "customers_write",
            "PATCH",
            "/api/v1/customers/{customer_id}",
            ("sales.customers.write",),
            customer_patch_body,
            ("customer_id",),
        ),
        ProbeSpec(
            "customers_delete",
            "DELETE",
            "/api/v1/customers/{customer_id}",
            ("sales.customers.delete",),
            lambda _: None,
            ("customer_id",),
        ),
        ProbeSpec(
            "purchases_create",
            "POST",
            "/api/v1/purchases",
            ("warehouse.purchases.write",),
            purchase_create_body,
            ("supplier_id", "product_id"),
        ),
        ProbeSpec(
            "purchases_delete",
            "DELETE",
            "/api/v1/purchases/{purchase_id}",
            ("warehouse.purchases.delete",),
            lambda _: None,
            ("purchase_id",),
        ),
        ProbeSpec(
            "inventory_write",
            "PATCH",
            "/api/v1/inventory/{product_id}",
            ("warehouse.inventory.write",),
            inventory_patch_body,
            ("product_id",),
        ),
        ProbeSpec(
            "inventory_delete",
            "DELETE",
            "/api/v1/inventory/{product_id}",
            ("warehouse.inventory.delete",),
            lambda _: None,
            ("product_id",),
        ),
        ProbeSpec(
            "suppliers_write",
            "POST",
            "/api/v1/suppliers",
            ("warehouse.suppliers.write",),
            supplier_create_body,
        ),
        ProbeSpec(
            "suppliers_delete",
            "DELETE",
            "/api/v1/suppliers/{supplier_id}",
            ("warehouse.suppliers.delete",),
            lambda _: None,
            ("supplier_id",),
        ),
        ProbeSpec(
            "documents_write",
            "POST",
            "/api/v1/erp-documents",
            ("warehouse.documents.write",),
            document_create_body,
        ),
        ProbeSpec(
            "documents_delete",
            "DELETE",
            "/api/v1/erp-documents/{document_id}",
            ("warehouse.documents.delete",),
            lambda _: None,
            ("document_id",),
        ),
        ProbeSpec(
            "bom_write",
            "POST",
            "/api/v1/bom/{product_sku}",
            ("warehouse.bom.write",),
            bom_write_body,
            ("product_sku",),
        ),
        ProbeSpec(
            "material_rolls_write",
            "POST",
            "/api/v1/material-rolls",
            ("warehouse.material_rolls.write",),
            material_roll_body,
            ("product_id",),
        ),
        ProbeSpec(
            "procurement_ai",
            "POST",
            "/api/v1/procurement-runs",
            ("warehouse.procurement.manage",),
            procurement_body,
        ),
        ProbeSpec(
            "crm_leads_write",
            "POST",
            "/api/v1/crm/leads",
            ("crm.leads.write",),
            crm_lead_body,
        ),
        ProbeSpec(
            "crm_opps_write",
            "POST",
            "/api/v1/crm/opportunities",
            ("crm.opportunities.write",),
            crm_opp_body,
            ("customer_id",),
        ),
        ProbeSpec(
            "payments_write",
            "POST",
            "/api/v1/payments/receive",
            ("finance.payments.write", "finance.records.write"),
            payment_receive_body,
            ("customer_id", "payment_method_id"),
        ),
        ProbeSpec(
            "payments_approve",
            "POST",
            "/api/v1/payments/{payment_id}/confirm",
            (
                "finance.payments.approve",
                "finance.payments.write",
                "finance.records.write",
            ),
            lambda _: None,
            ("payment_id",),
        ),
        ProbeSpec(
            "tax_write",
            "POST",
            "/api/v1/tax-rates",
            ("finance.tax.write", "finance.records.write"),
            tax_create_body,
        ),
        ProbeSpec(
            "mfg_write",
            "POST",
            "/api/v1/manufacturing/production-orders",
            ("manufacturing.ops.write", "manufacturing.master.write"),
            mfg_po_body,
            ("product_id",),
        ),
        ProbeSpec(
            "mfg_plan_write",
            "POST",
            "/api/v1/manufacturing/planning/plans",
            ("manufacturing.planning.write", "manufacturing.ops.write"),
            mfg_plan_body,
        ),
        ProbeSpec(
            "mfg_work_center_write",
            "POST",
            "/api/v1/manufacturing/work-centers",
            ("manufacturing.ops.write", "manufacturing.master.write"),
            mfg_wc_body,
        ),
        ProbeSpec(
            "access_users_list",
            "GET",
            "/api/v1/access/users",
            ("system.users.read", "system.users.manage"),
            lambda _: None,
        ),
        ProbeSpec(
            "access_roles_matrix",
            "PUT",
            "/api/v1/access/roles/{role_id}/permissions",
            ("system.roles.manage",),
            access_roles_body,
            ("role_id",),
        ),
        ProbeSpec(
            "layout_configure",
            "PATCH",
            "/api/v1/users/me/preferences",
            ("profile.layout.configure",),
            layout_body,
        ),
        ProbeSpec(
            "dashboard_read",
            "GET",
            "/api/v1/dashboard/summary",
            ("reports.dashboard.read",),
            lambda _: None,
        ),
    )


PROBES = _build_probes()

REQUIRED_FIXTURE_FIELDS: frozenset[str] = frozenset(
    field for probe in PROBES for field in probe.fixture_fields
)


@dataclass
class ProbeRow:
    user_email: str
    role_name: str
    probe_key: str
    required_permissions: str
    has_permission: bool
    probe_mode: str
    http_status: int | None
    result: str
    detail: str = ""


def _resolve_path(path_template: str, fixtures: FixtureIds) -> str:
    path = path_template
    for key, value in fixtures.__dict__.items():
        if value is not None:
            path = path.replace(f"{{{key}}}", str(value))
    return path


async def _load_bearer_tokens(emails: tuple[str, ...]) -> dict[str, str]:
    tokens: dict[str, str] = {}
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email.in_(emails)))
        for user in result.scalars().all():
            tokens[user.email] = create_access_token(str(user.id), role=user.role.value)
    return tokens


async def _prepare_session(
    emails: tuple[str, ...],
    *,
    load_tokens: bool,
) -> tuple[FixtureIds, dict[str, str]]:
    await init_db()
    fixtures = await _bootstrap_fixtures_db()
    tokens = await _load_bearer_tokens(emails) if load_tokens else {}
    return fixtures, tokens


def _login(
    client: httpx.Client,
    email: str,
    password: str,
    *,
    use_http_login: bool,
    bearer_tokens: dict[str, str],
) -> tuple[set[str], str | None]:
    if use_http_login:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        if response.status_code != 200:
            return set(), f"login failed ({response.status_code})"
        data = response.json()
        return set(data.get("permissions") or []), None

    token = bearer_tokens.get(email)
    if token is None:
        return set(), "user not found in database"
    client.headers["Authorization"] = f"Bearer {token}"
    return set(), None


def _fetch_permissions(client: httpx.Client) -> set[str]:
    response = client.get("/api/v1/auth/me/permissions")
    if response.status_code != 200:
        return set()
    return set(response.json().get("permissions") or [])


def _first_id(client: httpx.Client, path: str, key: str = "items") -> int | None:
    response = client.get(path)
    if response.status_code != 200:
        return None
    data = response.json()
    items = data.get(key) if isinstance(data, dict) else data
    if not items:
        return None
    first = items[0]
    if isinstance(first, dict) and "id" in first:
        return int(first["id"])
    return None


async def _create_minimal_purchase_sql(
    db,
    *,
    supplier_id: int,
    product_id: int,
    unit_cost: str,
    admin_id: int,
) -> int:
    purchase_id = (
        await db.execute(
            text(
                """
                INSERT INTO purchases (
                    supplier_id, created_by_id, status, total, amount_paid,
                    payment_status, currency_code
                )
                VALUES (
                    :supplier_id, :admin_id, 'DRAFT', 0, 0, 'UNPAID', 'USD'
                )
                RETURNING id
                """
            ),
            {"supplier_id": supplier_id, "admin_id": admin_id},
        )
    ).scalar_one()
    await db.execute(
        text(
            """
            INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_cost)
            VALUES (:purchase_id, :product_id, 1, :unit_cost)
            """
        ),
        {
            "purchase_id": purchase_id,
            "product_id": product_id,
            "unit_cost": unit_cost,
        },
    )
    return int(purchase_id)


async def _bootstrap_fixtures_db() -> FixtureIds:
    """Create or load all fixture IDs required by probes (no HTTP)."""
    fixtures = FixtureIds()
    async with AsyncSessionLocal() as db:
        await seed_admin_user(db)
        try:
            demo_result = await seed_agent_demo_data(db)
            if not demo_result.get("skipped"):
                await db.commit()
        except Exception:
            await db.rollback()
        await db.commit()

    async with AsyncSessionLocal() as db:
        admin = (
            await db.execute(select(User).where(User.email == SUPER_ADMIN_EMAIL))
        ).scalar_one_or_none()
        if admin is None:
            admin = (await db.execute(select(User).where(User.role == UserRole.ADMIN).limit(1))).scalar_one()

        product = (
            await db.execute(
                select(Product)
                .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE)
                .order_by(Product.id)
                .limit(1),
            )
        ).scalar_one_or_none()
        if product is None:
            raise RuntimeError("No active product in database for probe fixtures")

        customer = (await db.execute(select(Customer).order_by(Customer.id).limit(1))).scalar_one_or_none()
        supplier = (await db.execute(select(Supplier).order_by(Supplier.id).limit(1))).scalar_one_or_none()
        if customer is None or supplier is None:
            raise RuntimeError("Missing customer or supplier for probe fixtures")

        fixtures.product_id = product.id
        fixtures.product_sku = product.sku
        fixtures.customer_id = customer.id
        fixtures.supplier_id = supplier.id

        sale_id = await db.scalar(select(func.max(Sale.id)))
        if sale_id is None:
            sale = await sale_crud.create_sale_order(
                db,
                SaleOrderCreate(
                    items=[SaleItemLineCreate(product_id=product.id, quantity=1)],
                    confirm=False,
                ),
                created_by_id=admin.id,
                allow_price_override=True,
            )
            sale_id = sale.id
        fixtures.sale_id = int(sale_id)

        purchase_id = await db.scalar(select(func.max(Purchase.id)))
        if purchase_id is None:
            purchase_id = await _create_minimal_purchase_sql(
                db,
                supplier_id=supplier.id,
                product_id=product.id,
                unit_cost=str(product.price or "1.00"),
                admin_id=admin.id,
            )
        fixtures.purchase_id = int(purchase_id)

        from app.models.erp_document import ErpDocument

        document = (await db.execute(select(ErpDocument).order_by(ErpDocument.id.desc()).limit(1))).scalar_one_or_none()
        if document is None:
            document = await erp_document_crud.create_erp_document(
                db,
                ErpDocumentCreate(
                    document_type=ErpDocumentType.TECH_PACK,
                    title="RBAC probe fixture document",
                    status=ErpDocumentStatus.DRAFT,
                ),
                created_by_id=admin.id,
            )
            await db.commit()
        fixtures.document_id = document.id

        payment_method = (
            await db.execute(select(PaymentMethod).order_by(PaymentMethod.id).limit(1))
        ).scalar_one_or_none()
        if payment_method is None:
            raise RuntimeError("No payment method in database for probe fixtures")
        fixtures.payment_method_id = payment_method.id

        payment = (
            await db.execute(
                select(Payment).order_by(Payment.id.desc()).limit(1),
            )
        ).scalar_one_or_none()
        if payment is None:
            payment = await payment_service.receive_payment(
                db,
                ReceivePaymentCreate(
                    customer_id=customer.id,
                    payment_method_id=payment_method.id,
                    amount="1.00",
                    payment_date=date.today(),
                ),
                created_by_id=admin.id,
            )
            payment = await payment_service.submit_for_approval(db, payment.id, user_id=admin.id)
        fixtures.payment_id = payment.id

        role = (await db.execute(select(Role).order_by(Role.id).limit(1))).scalar_one_or_none()
        if role is None:
            raise RuntimeError("No role in database for probe fixtures")
        fixtures.role_id = role.id

        await db.commit()

    return fixtures


def _validate_fixtures(fixtures: FixtureIds) -> list[str]:
    return [name for name in sorted(REQUIRED_FIXTURE_FIELDS) if getattr(fixtures, name) is None]


def _ensure_draft_sale(client: httpx.Client, product_id: int | None) -> int | None:
    existing = _first_id(client, "/api/v1/sales?limit=1")
    if existing is not None:
        return existing
    if product_id is None:
        return None
    response = client.post(
        "/api/v1/sales",
        json={
            "items": [{"product_id": product_id, "quantity": 1}],
            "confirm": False,
        },
    )
    if response.status_code not in (200, 201):
        return None
    return response.json().get("id")


def _ensure_draft_purchase(
    client: httpx.Client,
    supplier_id: int | None,
    product_id: int | None,
) -> int | None:
    existing = _first_id(client, "/api/v1/purchases?limit=1")
    if existing is not None:
        return existing
    if supplier_id is None or product_id is None:
        return None
    response = client.post(
        "/api/v1/purchases",
        json={
            "supplier_id": supplier_id,
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )
    if response.status_code not in (200, 201):
        return None
    return response.json().get("id")


def _ensure_document(client: httpx.Client) -> int | None:
    existing = _first_id(client, "/api/v1/erp-documents?limit=1")
    if existing is not None:
        return existing
    response = client.post(
        "/api/v1/erp-documents",
        json={
            "document_type": "TECH_PACK",
            "title": "RBAC probe bootstrap document",
            "status": "DRAFT",
        },
    )
    if response.status_code not in (200, 201):
        return None
    return response.json().get("id")


def _bootstrap_fixtures(client: httpx.Client) -> FixtureIds:
    fixtures = FixtureIds()
    fixtures.product_id = _first_id(client, "/api/v1/inventory?limit=1")
    fixtures.sale_id = _ensure_draft_sale(client, fixtures.product_id)
    fixtures.customer_id = _first_id(client, "/api/v1/customers?limit=1")
    fixtures.supplier_id = _first_id(client, "/api/v1/suppliers?limit=1")
    fixtures.purchase_id = _ensure_draft_purchase(
        client,
        fixtures.supplier_id,
        fixtures.product_id,
    )
    fixtures.document_id = _ensure_document(client)
    fixtures.payment_id = _first_id(client, "/api/v1/payments?limit=1")
    fixtures.payment_method_id = _first_id(client, "/api/v1/payment-methods?limit=1")
    fixtures.lead_id = _first_id(client, "/api/v1/crm/leads?limit=1")

    roles_resp = client.get("/api/v1/access/roles")
    if roles_resp.status_code == 200:
        roles = roles_resp.json()
        if roles:
            fixtures.role_id = int(roles[0]["id"])

    if fixtures.product_id is not None:
        prod_resp = client.get(f"/api/v1/inventory/{fixtures.product_id}")
        if prod_resp.status_code == 200:
            fixtures.product_sku = prod_resp.json().get("sku")

    return fixtures


def _classify_negative(http_status: int | None, detail: str) -> str:
    if http_status is None:
        return "FAIL"
    if http_status == 403:
        return "SECURE"
    if 200 <= http_status < 300:
        return "BREACH"
    if http_status == 401:
        return "FAIL"
  # Passed auth layer but failed business validation — still unauthorized grant
    if http_status in (400, 404, 409, 422):
        return "BREACH"
    return "FAIL"


def _classify_positive(http_status: int | None, detail: str) -> str:
    if http_status is None:
        return "FAIL"
    if http_status == 403:
        return "DENY_UNEXPECTED"
    if http_status in (401,):
        return "FAIL"
    return "ALLOW_OK"


def _execute_probe(
    client: httpx.Client,
    probe: ProbeSpec,
    fixtures: FixtureIds,
) -> tuple[int | None, str]:
    missing = _missing_fixtures(fixtures, probe.fixture_fields)
    if missing:
        raise RuntimeError(f"Probe {probe.key} missing fixtures: {', '.join(missing)}")

    body = probe.body(fixtures)
    if body is None:
        if probe.method in ("POST", "PATCH", "PUT"):
            body = {}
        elif probe.method != "DELETE" and probe.fixture_fields:
            raise RuntimeError(f"Probe {probe.key} could not build request body")

    path = _resolve_path(probe.path, fixtures)
    if "{" in path:
        raise RuntimeError(f"Probe {probe.key} unresolved path: {path}")

    request = client.build_request(
        probe.method,
        path,
        json=body if probe.method in ("POST", "PATCH", "PUT") else None,
    )
    response = client.send(request)
    return response.status_code, ""


def _filter_users(indices: set[int] | None) -> tuple[SeedUserSpec, ...]:
    if not indices:
        return SEED_USERS
    return tuple(u for u in SEED_USERS if u.index in indices)


def _write_report(rows: list[ProbeRow], output_path: Path, csv_path: Path | None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    secure = sum(1 for r in rows if r.result == "SECURE")
    breach = [r for r in rows if r.result == "BREACH"]
    allow_ok = sum(1 for r in rows if r.result == "ALLOW_OK")
    deny_unexpected = [r for r in rows if r.result == "DENY_UNEXPECTED"]
    failed = [r for r in rows if r.result == "FAIL"]

    lines = [
        "# RBAC permission breach probe report",
        "",
        f"Total probe executions: **{len(rows)}**",
        f"- SECURE (no permission → 403): **{secure}**",
        f"- BREACH (no permission → allowed): **{len(breach)}**",
        f"- ALLOW_OK (has permission → not 403): **{allow_ok}**",
        f"- DENY_UNEXPECTED (has permission → 403): **{len(deny_unexpected)}**",
        f"- FAIL (setup/auth error): **{len(failed)}**",
        "",
    ]

    if breach:
        lines.append("## Breaches detected")
        lines.append("")
        lines.append("| User | Role | Probe | Required | HTTP |")
        lines.append("|------|------|-------|----------|------|")
        for r in breach:
            lines.append(
                f"| {r.user_email} | {r.role_name} | {r.probe_key} | {r.required_permissions} | {r.http_status} |"
            )
        lines.append("")
    else:
        lines.append("## Breaches detected")
        lines.append("")
        lines.append("None — every unauthorized probe returned 403.")
        lines.append("")

    if deny_unexpected:
        lines.append("## Unexpected denials (has permission but 403)")
        lines.append("")
        lines.append("| User | Role | Probe | HTTP |")
        lines.append("|------|------|-------|------|")
        for r in deny_unexpected[:50]:
            lines.append(f"| {r.user_email} | {r.role_name} | {r.probe_key} | {r.http_status} |")
        if len(deny_unexpected) > 50:
            lines.append(f"| … | | | ({len(deny_unexpected) - 50} more) |")
        lines.append("")

    lines.append("## Full results")
    lines.append("")
    lines.append(
        "| User | Role | Probe | Mode | Required perm | Has perm? | HTTP | Result | Detail |"
    )
    lines.append(
        "|------|------|-------|------|---------------|-----------|------|--------|--------|"
    )

    current_email = ""
    for r in rows:
        if r.user_email != current_email:
            current_email = r.user_email
            lines.append("")
        has = "yes" if r.has_permission else "no"
        http = str(r.http_status) if r.http_status is not None else "-"
        detail = r.detail.replace("|", "\\|")
        lines.append(
            f"| {r.user_email} | {r.role_name} | {r.probe_key} | {r.probe_mode} | "
            f"{r.required_permissions} | {has} | {http} | {r.result} | {detail} |"
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")

    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "user_email",
                    "role_name",
                    "probe_key",
                    "probe_mode",
                    "required_permissions",
                    "has_permission",
                    "http_status",
                    "result",
                    "detail",
                ],
            )
            writer.writeheader()
            for r in rows:
                writer.writerow(
                    {
                        "user_email": r.user_email,
                        "role_name": r.role_name,
                        "probe_key": r.probe_key,
                        "probe_mode": r.probe_mode,
                        "required_permissions": r.required_permissions,
                        "has_permission": r.has_permission,
                        "http_status": r.http_status or "",
                        "result": r.result,
                        "detail": r.detail,
                    }
                )


def run_probe(
    *,
    base_url: str,
    password: str,
    output: Path,
    csv_output: Path | None,
    user_indices: set[int] | None,
    login_delay: float,
    use_http_login: bool,
) -> int:
    base = base_url.rstrip("/")
    health_url = f"{base}/api/v1/health"
    try:
        health = httpx.get(health_url, timeout=5.0)
    except httpx.HTTPError as exc:
        print(f"API not reachable at {base_url}: {exc}", file=sys.stderr)
        print("Start the backend: cd backend && uvicorn app.main:app --reload", file=sys.stderr)
        return 1

    if health.status_code != 200:
        print(f"API health check failed: {health.status_code}", file=sys.stderr)
        return 1

    rows: list[ProbeRow] = []
    users = _filter_users(user_indices)
    emails = tuple({SUPER_ADMIN_EMAIL, *(u.email for u in users)})

    try:
        fixtures, bearer_tokens = asyncio.run(
            _prepare_session(emails, load_tokens=not use_http_login),
        )
    except Exception as exc:
        print(f"Fixture bootstrap failed: {exc}", file=sys.stderr)
        return 1

    if not use_http_login and SUPER_ADMIN_EMAIL not in bearer_tokens:
        print(
            f"Super-admin not found ({SUPER_ADMIN_EMAIL}). "
            "Run: python3 scripts/seed_rbac_users.py",
            file=sys.stderr,
        )
        return 1

    missing = _validate_fixtures(fixtures)
    if missing:
        print(f"Fixture bootstrap incomplete: {', '.join(missing)}", file=sys.stderr)
        return 1

    print(f"Bootstrap fixtures: {fixtures}")

    for index, user_spec in enumerate(users):
        if index > 0 and login_delay > 0:
            time.sleep(login_delay)

        with httpx.Client(base_url=base_url, timeout=60.0, follow_redirects=True) as client:
            perms, err = _login(
                client,
                user_spec.email,
                password,
                use_http_login=use_http_login,
                bearer_tokens=bearer_tokens,
            )
            if err:
                print(f"Login failed for {user_spec.email}: {err}", file=sys.stderr)
                return 1

            perms = _fetch_permissions(client) or perms

            for probe in PROBES:
                has_perm = _has_any_permission(perms, probe.required_permissions)
                try:
                    status_code, detail = _execute_probe(client, probe, fixtures)
                except RuntimeError as exc:
                    print(str(exc), file=sys.stderr)
                    return 1

                if not detail and status_code is not None:
                    detail = f"HTTP {status_code}"

                if has_perm:
                    result = _classify_positive(status_code, detail)
                    mode = "positive"
                else:
                    result = _classify_negative(status_code, detail)
                    mode = "negative"

                rows.append(
                    ProbeRow(
                        user_email=user_spec.email,
                        role_name=user_spec.role_name,
                        probe_key=probe.key,
                        required_permissions="|".join(probe.required_permissions),
                        has_permission=has_perm,
                        probe_mode=mode,
                        http_status=status_code,
                        result=result,
                        detail=detail,
                    )
                )

        print(f"Probed {user_spec.email} ({user_spec.role_name})")

    _write_report(rows, output, csv_output)

    breach_count = sum(1 for r in rows if r.result == "BREACH")
    secure_count = sum(1 for r in rows if r.result == "SECURE")
    deny_count = sum(1 for r in rows if r.result == "DENY_UNEXPECTED")
    fail_count = sum(1 for r in rows if r.result == "FAIL")
    allow_count = sum(1 for r in rows if r.result == "ALLOW_OK")
    print(f"\nReport written to {output}")
    print(
        f"SECURE: {secure_count}, ALLOW_OK: {allow_count}, "
        f"BREACH: {breach_count}, DENY_UNEXPECTED: {deny_count}, FAIL: {fail_count}"
    )
    if breach_count or deny_count or fail_count:
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="RBAC negative authorization probe (seed users)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--csv", type=Path, default=None, help="Optional CSV output path")
    parser.add_argument(
        "--users",
        default="",
        help="Comma-separated seed user indices (e.g. 11,9,5). Default: all 50.",
    )
    parser.add_argument(
        "--login-delay",
        type=float,
        default=13.0,
        help="Seconds between user logins when using --http-login (auth rate limit is 5/minute)",
    )
    parser.add_argument(
        "--http-login",
        action="store_true",
        help="Authenticate via POST /auth/login (default: mint Bearer JWT from DB, no rate limit)",
    )
    args = parser.parse_args()

    indices: set[int] | None = None
    if args.users.strip():
        indices = {int(x.strip()) for x in args.users.split(",") if x.strip()}

    csv_path = args.csv
    if csv_path is None:
        csv_path = args.output.with_suffix(".csv")

    exit_code = run_probe(
        base_url=args.base_url,
        password=args.password,
        output=args.output,
        csv_output=csv_path,
        user_indices=indices,
        login_delay=args.login_delay if args.http_login else 0.0,
        use_http_login=args.http_login,
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
