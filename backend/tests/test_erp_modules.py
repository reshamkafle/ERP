from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import module_record as module_record_crud
from app.models.module_record import ModuleRecord
from app.modules.catalog import MODULE_CATALOG
from app.modules.seed import seed_module_records_if_empty
from app.schemas.module_record import ModuleRecordCreate, ModuleRecordUpdate
from app.services.module_overview import build_module_overview


def test_module_catalog_has_eleven_modules() -> None:
    assert len(MODULE_CATALOG) == 11
    codes = {m.code for m in MODULE_CATALOG}
    assert codes == {
        "finance",
        "hcm",
        "procurement",
        "warehouse",
        "scm",
        "tms",
        "manufacturing",
        "sales",
        "crm",
        "projects",
        "platform",
    }


@pytest.mark.asyncio
async def test_seed_and_overview(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()
    created = await seed_module_records_if_empty(db_session)
    assert created > 0

    overview = await build_module_overview(db_session, "finance")
    assert overview is not None
    assert overview.module_code == "finance"
    assert overview.total_records > 0
    assert len(overview.features) == 8

    count = (
        await db_session.execute(
            select(func.count()).select_from(ModuleRecord).where(ModuleRecord.module_code == "hcm")
        )
    ).scalar_one()
    assert count == 7


@pytest.mark.asyncio
async def test_hcm_employee_extra_data_round_trip(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()

    extra = {
        "employee": {
            "personal": {
                "employee_id": "EMP-TEST-99",
                "first_name": "Casey",
                "last_name": "Nguyen",
            },
            "employment": {
                "department": "Engineering",
                "hire_date": "2025-06-01",
            },
        },
    }
    created = await module_record_crud.create_module_record(
        db_session,
        "hcm",
        ModuleRecordCreate(
            feature_code="employee_records",
            reference="EMP-TEST-99",
            title="Casey Nguyen",
            status="ACTIVE",
            party_name="Pat Manager",
            amount=Decimal("7200.00"),
            start_date=None,
            end_date=None,
            extra_data=extra,
        ),
    )
    await db_session.flush()

    loaded = await module_record_crud.get_module_record(db_session, created.id)
    assert loaded is not None
    assert loaded.extra_data is not None
    personal = loaded.extra_data["employee"]["personal"]
    assert personal["employee_id"] == "EMP-TEST-99"
    assert personal["first_name"] == "Casey"

    await module_record_crud.update_module_record(
        db_session,
        loaded,
        ModuleRecordUpdate(
            extra_data={
                **extra,
                "employee": {
                    **extra["employee"],
                    "personal": {**personal, "preferred_name": "Case"},
                },
            },
        ),
    )
    await db_session.flush()
    reloaded = await module_record_crud.get_module_record(db_session, created.id)
    assert reloaded is not None
    assert reloaded.extra_data["employee"]["personal"]["preferred_name"] == "Case"


@pytest.mark.asyncio
async def test_manufacturing_production_extra_data_round_trip(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()

    extra = {
        "production": {
            "overview": {
                "process_type": "batch",
                "flow_description": "Weave → dye → cut",
                "stage": "pilot",
            },
            "facility": {"plant_location": "Plant B"},
            "capacity": {"utilized_pct": "65"},
            "machinery": [{"name": "Loom line 2", "capacity": "500 m/day"}],
        },
    }
    created = await module_record_crud.create_module_record(
        db_session,
        "manufacturing",
        ModuleRecordCreate(
            feature_code="production_orders",
            reference="PO-TEST-01",
            title="Pilot batch — Plant B",
            status="DRAFT",
            start_date=None,
            end_date=None,
            extra_data=extra,
        ),
    )
    await db_session.flush()

    loaded = await module_record_crud.get_module_record(db_session, created.id)
    assert loaded is not None
    assert loaded.extra_data is not None
    assert loaded.extra_data["production"]["facility"]["plant_location"] == "Plant B"

    await module_record_crud.update_module_record(
        db_session,
        loaded,
        ModuleRecordUpdate(
            extra_data={
                **extra,
                "production": {
                    **extra["production"],
                    "capacity": {"utilized_pct": "80"},
                },
            },
        ),
    )
    await db_session.flush()
    reloaded = await module_record_crud.get_module_record(db_session, created.id)
    assert reloaded is not None
    assert reloaded.extra_data["production"]["capacity"]["utilized_pct"] == "80"


@pytest.mark.asyncio
async def test_tms_shipment_extra_data_round_trip(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()

    extra = {
        "basic": {
            "shipment_id": "SHP-TEST-01",
            "order_reference": "SO-2026-001",
            "shipment_type": "OUTBOUND",
            "shipment_date": "2026-05-20",
            "requested_delivery_date": "2026-05-25",
            "service_level": "STANDARD",
            "transport_mode": "ROAD",
        },
        "shipper": {"warehouse_code": "WH-01", "city": "Dallas"},
        "consignee": {"ship_to_location": "Store 12", "city": "Houston"},
        "line_items": [
            {
                "item_number": "SKU-001",
                "quantity": "10",
                "packaging_type": "CARTON",
            },
        ],
        "carrier": {
            "carrier_name": "FastFreight",
            "tracking_number": "PRO-12345",
            "freight_cost": "250.00",
        },
        "compliance": {"bol_number": "BOL-99"},
        "tracking": {"current_status": "IN_TRANSIT"},
        "financial": {"payment_status": "PENDING"},
    }
    created = await module_record_crud.create_module_record(
        db_session,
        "tms",
        ModuleRecordCreate(
            feature_code="shipments",
            reference="SHP-TEST-01",
            title="Outbound — Store 12",
            status="IN_TRANSIT",
            party_name="FastFreight",
            amount=Decimal("250.00"),
            start_date=None,
            end_date=None,
            extra_data=extra,
        ),
    )
    await db_session.flush()

    loaded = await module_record_crud.get_module_record(db_session, created.id)
    assert loaded is not None
    assert loaded.extra_data is not None
    assert loaded.extra_data["carrier"]["tracking_number"] == "PRO-12345"
    assert loaded.extra_data["line_items"][0]["item_number"] == "SKU-001"

    await module_record_crud.update_module_record(
        db_session,
        loaded,
        ModuleRecordUpdate(
            status="DELIVERED",
            extra_data={
                **extra,
                "tracking": {
                    **extra["tracking"],
                    "current_status": "DELIVERED",
                    "pod_reference": "POD-7788",
                },
            },
        ),
    )
    await db_session.flush()
    reloaded = await module_record_crud.get_module_record(db_session, created.id)
    assert reloaded is not None
    assert reloaded.status == "DELIVERED"
    assert reloaded.extra_data["tracking"]["pod_reference"] == "POD-7788"


@pytest.mark.asyncio
async def test_platform_industry_extra_data_round_trip(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()

    extra = {
        "identity": {"example_title": "Manufacturing Execution System - MES"},
        "industry": {
            "vertical": "Manufacturing",
            "core_gap_rationale": "Core modules lack shop-floor real-time tracking.",
        },
        "features": {
            "key_features": "BOM, Production Scheduling, Quality Control, OEE dashboards.",
        },
        "processes": {"business_processes": "Shop floor control, downtime capture, yield tracking."},
        "data_requirements": {
            "entities": "Items, recipes, work centers, routings",
            "core_integrations": "Manufacturing, Inventory, Finance",
        },
        "integration": {
            "erp_modules": "Manufacturing, Inventory",
            "third_party": "CAD, IoT PLCs",
            "apis": "REST + MQTT gateway",
        },
        "compliance": {
            "standards": "ISO 9001",
            "audit_trails": "Electronic batch records",
        },
        "reporting": {"dashboards_kpis": "Yield analysis, OEE, scrap rate"},
        "roles": {
            "user_roles": "Production supervisors, quality inspectors",
            "access_controls": "Role-based shop floor access",
        },
        "customization": {
            "configuration_needs": "Routing templates per product family",
            "low_code_tools": "Workflow designer",
        },
        "scalability": {
            "transaction_volume": "50k shop-floor events/day",
            "multi_site": "Multi-plant with shared BOM master",
        },
        "mobile": {"field_access": "Tablet apps for line operators"},
        "implementation": {
            "effort_estimate": "6 months",
            "migration": "Legacy MES CSV import",
            "training": "Supervisor and operator training",
            "go_live_dependencies": "Routing master data complete",
        },
        "costs": {
            "licensing": "120000",
            "implementation": "65000",
            "maintenance": "22000/year",
            "infrastructure": "15000",
        },
        "benefits": {
            "expected_outcomes": "Reduced downtime, improved yield",
            "roi_kpis": "OEE +8%, scrap -12%",
        },
        "risks": {
            "challenges": "Legacy data accuracy",
            "prerequisites": "Clean BOM and routing master",
        },
        "vendor": {
            "platform_fit": "Native ERP extension",
            "vendor_expertise": "Discrete manufacturing",
            "references": "3 similar MES rollouts",
        },
    }

    created = await module_record_crud.create_module_record(
        db_session,
        "platform",
        ModuleRecordCreate(
            feature_code="plant_maintenance",
            reference="PLT-TEST-01",
            title="Manufacturing Execution System - MES",
            status="IN_REVIEW",
            description="Shop-floor execution and OEE analytics for discrete manufacturing.",
            party_name="Manufacturing",
            amount=Decimal("185000.00"),
            quantity=None,
            start_date=None,
            end_date=None,
            extra_data=extra,
        ),
    )
    await db_session.flush()

    loaded = await module_record_crud.get_module_record(db_session, created.id)
    assert loaded is not None
    assert loaded.extra_data is not None
    assert loaded.extra_data["industry"]["vertical"] == "Manufacturing"
    assert loaded.extra_data["features"]["key_features"].startswith("BOM")

    await module_record_crud.update_module_record(
        db_session,
        loaded,
        ModuleRecordUpdate(
            status="APPROVED",
            extra_data={
                **extra,
                "benefits": {
                    **extra["benefits"],
                    "roi_kpis": "OEE +10%, scrap -15%",
                },
            },
        ),
    )
    await db_session.flush()

    reloaded = await module_record_crud.get_module_record(db_session, created.id)
    assert reloaded is not None
    assert reloaded.status == "APPROVED"
    assert reloaded.extra_data["benefits"]["roi_kpis"] == "OEE +10%, scrap -15%"
