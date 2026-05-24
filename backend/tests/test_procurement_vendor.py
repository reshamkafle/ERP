from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import module_record as module_record_crud
from app.crud import supplier as supplier_crud
from app.schemas.module_record import ModuleRecordCreate
from app.schemas.supplier import SupplierCreate, SupplierUpdate


@pytest.mark.asyncio
async def test_supplier_vendor_code_uniqueness(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()

    await supplier_crud.create_supplier(
        db_session,
        SupplierCreate(
            vendor_code="VND-TEST-001",
            name="Alpha Supplies",
            currency_code="USD",
        ),
    )

    with pytest.raises(ValueError, match="already exists"):
        await supplier_crud.create_supplier(
            db_session,
            SupplierCreate(
                vendor_code="VND-TEST-001",
                name="Duplicate Vendor",
                currency_code="USD",
            ),
        )


@pytest.mark.asyncio
async def test_supplier_create_with_master_fields(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()

    created = await supplier_crud.create_supplier(
        db_session,
        SupplierCreate(
            vendor_code="VND-FULL-001",
            name="Full Vendor Co",
            legal_name="Full Vendor LLC",
            payment_terms="Net 30",
            tax_id="TAX-99",
            bank_details={
                "account_number": "123456",
                "swift": "ABCDUS33",
                "beneficiary_name": "Full Vendor LLC",
            },
            vendor_type="STRATEGIC",
            approval_status="PREFERRED",
            performance_rating=Decimal("92.5"),
            lead_time_days=14,
            moq=Decimal("100"),
            currency_code="USD",
            pricing_currency="EUR",
            documents={"w9": "W9-2024-01"},
        ),
    )

    loaded = await supplier_crud.get_supplier(db_session, created.id)
    assert loaded is not None
    assert loaded.vendor_code == "VND-FULL-001"
    assert loaded.legal_name == "Full Vendor LLC"
    assert loaded.payment_terms == "Net 30"
    assert loaded.bank_details is not None
    assert loaded.bank_details["swift"] == "ABCDUS33"
    assert loaded.performance_rating == Decimal("92.5")
    assert loaded.lead_time_days == 14

    await supplier_crud.update_supplier(
        db_session,
        loaded,
        SupplierUpdate(approval_status="APPROVED", performance_rating=Decimal("95")),
    )
    reloaded = await supplier_crud.get_supplier(db_session, created.id)
    assert reloaded is not None
    assert reloaded.approval_status == "APPROVED"
    assert reloaded.performance_rating == Decimal("95")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "feature_code,prefix",
    [
        ("purchase_requisitions", "PR"),
        ("purchase_orders", "PO"),
        ("goods_receipt", "GRN"),
        ("invoice_matching", "INV"),
    ],
)
async def test_procurement_module_record_round_trip(
    db_session: AsyncSession,
    feature_code: str,
    prefix: str,
) -> None:
    from app.core.database import init_db

    await init_db()

    ref = f"{prefix}-TEST-ROUND"
    extra = {
        "header": {
            "requisition_number": ref if feature_code == "purchase_requisitions" else "",
            "po_number": ref if feature_code == "purchase_orders" else "",
            "grn_number": ref if feature_code == "goods_receipt" else "",
            "supplier_invoice_number": ref if feature_code == "invoice_matching" else "",
            "vendor_code": "VND-TEST",
        },
        "line_items": [
            {
                "item_code": "SKU-001",
                "description": "Widget",
                "quantity": "10",
                "uom": "EA",
            },
        ],
    }

    created = await module_record_crud.create_module_record(
        db_session,
        "procurement",
        ModuleRecordCreate(
            feature_code=feature_code,
            reference=ref,
            title=f"Test {feature_code}",
            status="DRAFT",
            party_name="Test Vendor",
            amount=Decimal("1500.00"),
            extra_data=extra,
        ),
    )
    await db_session.flush()

    loaded = await module_record_crud.get_module_record(db_session, created.id)
    assert loaded is not None
    assert loaded.module_code == "procurement"
    assert loaded.feature_code == feature_code
    assert loaded.extra_data is not None
    assert len(loaded.extra_data["line_items"]) == 1
    assert loaded.extra_data["line_items"][0]["item_code"] == "SKU-001"
