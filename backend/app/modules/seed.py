from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module_record import ModuleRecord
from app.modules.catalog import MODULE_CATALOG


def _hcm_extra_data(feature_code: str) -> dict:
    """Sample structured HR payloads for HCM demo records."""
    if feature_code == "employee_records":
        return {
            "employee": {
                "personal": {
                    "employee_id": "EMP-DEMO-001",
                    "first_name": "Alex",
                    "last_name": "Rivera",
                    "personal_email": "alex.rivera@example.com",
                },
                "employment": {
                    "department": "Human Resources",
                    "job_title": "HR Specialist",
                    "hire_date": "2024-03-15",
                    "employee_status": "ACTIVE",
                    "reporting_manager_name": "Jordan Lee",
                },
                "emergency_contacts": [
                    {"name": "Sam Rivera", "relationship": "Spouse", "phone": "+1-555-0100"},
                ],
            },
        }
    if feature_code == "payroll":
        return {
            "payroll": {
                "employee_reference": "EMP-DEMO-001",
                "pay_period": "2026-04",
                "gross_pay": "5500",
                "net_pay": "4200",
                "payslip_elements": [
                    {"element_code": "BASE", "description": "Base pay", "amount": "5000"},
                ],
            },
        }
    if feature_code == "recruitment":
        return {
            "recruitment": {
                "requisition_id": "REQ-2026-014",
                "candidate_name": "Taylor Kim",
                "stage": "Interview",
                "interview_scores": [
                    {"interviewer": "Jordan Lee", "round": "1", "score": "4.5"},
                ],
            },
        }
    if feature_code == "performance":
        return {
            "performance": {
                "employee_reference": "EMP-DEMO-001",
                "review_cycle": "FY2026 H1",
                "review_rating": "Exceeds expectations",
            },
        }
    if feature_code == "training":
        return {
            "training": {
                "employee_reference": "EMP-DEMO-001",
                "course_name": "Workplace Safety",
                "completion_status": "In progress",
            },
        }
    if feature_code == "time_attendance":
        return {
            "time_attendance": {
                "employee_reference": "EMP-DEMO-001",
                "timesheet_period": "2026-04",
                "leave_balance_snapshot": "12 days annual",
            },
        }
    if feature_code == "benefits":
        return {
            "benefits": {
                "employee_reference": "EMP-DEMO-001",
                "health_plan_id": "MED-PLUS",
                "enrollment_status": "Enrolled",
            },
        }
    return {"seed": True, "module": "hcm", "feature": feature_code}


def _manufacturing_extra_data(feature_code: str) -> dict:
    """Sample manufacturing_profile payloads for demo module records."""
    profile = {
        "master_data": {
            "item_master": {
                "item_code": "FG-DEMO-001",
                "description": "Demo finished garment",
                "uom": "EA",
                "item_category": "finished_goods",
                "default_warehouse": "MAIN",
            },
            "bom": {
                "bom_number": "BOM-DEMO-001",
                "version": "1.0",
                "yield_rate": "98",
                "lines": [
                    {
                        "component_code": "RM-FABRIC-01",
                        "qty_per_assembly": "2.5",
                        "scrap_pct": "3",
                    },
                ],
            },
            "routing": {
                "routing_code": "RT-DEMO-01",
                "routing_name": "Cut and sew",
                "parent_sku": "FG-DEMO-001",
                "operations": [
                    {
                        "sequence": "10",
                        "operation_name": "Cut",
                        "work_center": "WC-CUT",
                        "setup_time_minutes": "15",
                        "run_time_minutes": "5",
                    },
                ],
            },
        },
        "inventory": {
            "valuation_method": "MOVING_AVERAGE",
            "abc_class": "A",
            "reorder_level": "500",
        },
        "planning": {
            "mrp_horizon_days": "90",
            "production_status": "RELEASED",
        },
        "quality": {
            "plan_code": "QP-DEMO-01",
            "stage": "FINAL",
            "coa_required": "yes",
        },
        "costing": {
            "standard_cost": "12.50",
            "material_cost": "6.00",
            "labor_cost": "3.50",
        },
        "resources": {
            "work_center_code": "WC-CUT",
            "capacity": "800 units/day",
            "efficiency_pct": "78",
        },
        "supplier": {
            "approved_vendors": [
                {
                    "supplier_name": "Local Textiles Co.",
                    "lead_time_days": "14",
                },
            ],
        },
        "compliance": {
            "regulatory_codes": "ISO 9001",
            "country_of_origin": "BD",
        },
    }
    if feature_code == "bom_routing":
        return {"seed": True, "module": "manufacturing", "feature": feature_code, "manufacturing_profile": profile}
    if feature_code == "quality_management":
        profile["quality"]["templates"] = [
            {"characteristic": "Seam strength", "min_value": "50", "max_value": "80", "tolerance": "N"},
        ]
        return {"seed": True, "module": "manufacturing", "feature": feature_code, "manufacturing_profile": profile}
    return {"seed": True, "module": "manufacturing", "feature": feature_code, "manufacturing_profile": profile}


def _tms_extra_data(feature_code: str) -> dict:
    if feature_code == "shipments":
        return {
            "basic": {
                "shipment_id": "SHP-DEMO-001",
                "order_reference": "SO-2026-0042",
                "shipment_type": "OUTBOUND",
                "shipment_date": "2026-05-20",
                "requested_delivery_date": "2026-05-25",
                "service_level": "STANDARD",
                "transport_mode": "ROAD",
            },
            "shipper": {
                "warehouse_code": "WH-MAIN",
                "street": "100 Industrial Blvd",
                "city": "Dallas",
                "state": "TX",
                "zip": "75201",
                "country": "US",
                "contact_name": "Maria Chen",
                "contact_phone": "+1-555-0200",
                "loading_appointment": "2026-05-20",
                "loading_time_window": "08:00–12:00",
            },
            "consignee": {
                "ship_to_location": "Acme Retail — Store 12",
                "street": "450 Commerce Way",
                "city": "Houston",
                "state": "TX",
                "zip": "77002",
                "country": "US",
                "contact_name": "James Ortiz",
                "contact_phone": "+1-555-0300",
                "delivery_appointment": "2026-05-22",
                "delivery_time_window": "13:00–17:00",
            },
            "line_items": [
                {
                    "item_number": "SKU-WIDGET-01",
                    "item_description": "Widget assembly kit",
                    "quantity": "24",
                    "weight_per_unit": "2.5",
                    "weight_total": "60",
                    "length": "12",
                    "width": "8",
                    "height": "6",
                    "volume": "576",
                    "packaging_type": "CARTON",
                    "hazardous_material": "NO",
                },
            ],
            "carrier": {
                "carrier_name": "FastFreight Logistics",
                "carrier_code": "FFL",
                "carrier_service": "LTL Standard",
                "quoted_rate": "425.00",
                "freight_cost": "398.50",
                "accessorial_charges": "Fuel surcharge $45; Liftgate $35",
                "tracking_number": "PRO-8847291",
            },
            "compliance": {
                "bol_number": "BOL-2026-5512",
                "customs_compliance_data": "",
                "insurance_value": "5000",
                "special_instructions": "Call consignee 30 min before arrival.",
                "label_requirements": "Carrier standard 4x6 shipping label",
            },
            "tracking": {
                "current_status": "IN_TRANSIT",
                "eta": "2026-05-22T15:00",
                "actual_pickup_datetime": "2026-05-20T09:15",
                "actual_delivery_datetime": "",
                "pod_reference": "",
                "exception_reason": "",
            },
            "financial": {
                "freight_bill_amount": "398.50",
                "carrier_invoice_number": "INV-FFL-9921",
                "payment_status": "PENDING",
                "cost_center": "CC-LOG-01",
                "custom_fields": "",
            },
        }
    return {"seed": True, "module": "tms", "feature": feature_code}


def _crm_extra_data(feature_code: str) -> dict:
    if feature_code == "marketing_campaigns":
        return {
            "campaign": {
                "channel": "email",
                "segment": "VIP customers",
                "budget": "5000",
                "expected_roi_pct": "12",
            },
        }
    if feature_code == "customer_service":
        return {
            "case": {
                "case_type": "warranty",
                "priority": "high",
                "sla_hours": "24",
                "knowledge_article": "KB-WARRANTY-001",
            },
        }
    if feature_code == "support_tickets":
        return {
            "ticket": {
                "category": "billing",
                "sla_due": "2026-05-25",
                "escalation_level": "1",
            },
        }
    if feature_code == "contacts":
        return {
            "contact": {
                "preferred_channel": "EMAIL",
                "influence_level": "DECISION_MAKER",
            },
        }
    if feature_code == "sales_pipeline":
        return {
            "pipeline": {
                "stage": "QUALIFICATION",
                "probability": "40",
                "source": "trade_show",
            },
        }
    return {"seed": True, "module": "crm", "feature": feature_code}


def _projects_extra_data(feature_code: str) -> dict:
    if feature_code == "project_planning":
        return {
            "master_data": {
                "project_code": "PRJ-DEMO-001",
                "project_type": "FIXED_PRICE",
                "project_category": "IT_SOFTWARE",
                "start_date": "2026-03-01",
                "end_date": "2026-09-30",
                "expected_duration_days": "214",
                "project_manager": "Sarah Nguyen",
                "project_sponsor": "David Chen",
                "client_name": "Acme Retail Group",
                "client_contact": "James Ortiz",
                "client_email": "j.ortiz@acme.example",
                "objectives": "Deliver ERP integration and rollout for retail operations.",
                "scope_statement": "Phase 1: inventory, sales, and finance modules.",
                "priority_level": "HIGH",
                "strategic_alignment": "Digital transformation initiative FY2026",
            },
            "planning": {
                "wbs_root": "1.0",
                "critical_path_summary": "Requirements → Build → UAT → Go-live",
                "gantt_notes": "Baseline schedule approved 2026-03-15",
                "schedule_baseline": "BL-2026-001",
            },
            "tasks": [
                {
                    "wbs_code": "1.1",
                    "task_name": "Requirements gathering",
                    "dependency_type": "FINISH_TO_START",
                    "predecessor_task": "",
                    "estimated_duration_days": "20",
                    "estimated_effort_hours": "160",
                    "planned_start": "2026-03-01",
                    "planned_end": "2026-03-28",
                    "status": "COMPLETED",
                    "percent_complete": "100",
                },
            ],
            "milestones": [
                {
                    "milestone_code": "M1",
                    "milestone_name": "Design sign-off",
                    "due_date": "2026-04-15",
                    "status": "COMPLETED",
                },
            ],
            "resources": {
                "resource_calendar": "Standard business hours; no holidays in Q2 blackout.",
                "utilization_report_notes": "Team at 85% utilization in April.",
            },
            "resource_allocations": [
                {
                    "resource_type": "HUMAN",
                    "resource_name": "Dev team — squad A",
                    "allocation_percent": "100",
                    "cost_rate": "85",
                },
            ],
            "team_members": [
                {
                    "member_name": "Sarah Nguyen",
                    "role": "Project Manager",
                    "email": "s.nguyen@example.com",
                    "allocation_percent": "50",
                },
            ],
            "budget": {
                "total_budget": "250000",
                "budgeted_labor": "180000",
                "budgeted_material": "15000",
                "budgeted_overhead": "35000",
                "budgeted_travel": "20000",
                "actual_cost": "95000",
                "cost_variance": "-5000",
                "forecast_cost_to_complete": "240000",
            },
            "cost_lines": [
                {
                    "cost_category": "Labor",
                    "budgeted_amount": "180000",
                    "actual_amount": "72000",
                    "variance": "-8000",
                },
            ],
            "financial": {
                "chart_of_accounts": "COA-PROJECT-001",
                "gl_account": "4100-PRJ",
                "cost_center": "CC-IT-DEV",
            },
            "risk": {
                "change_request_process": "CR submitted via PMO portal; sponsor approval required.",
            },
            "risks": [
                {
                    "risk_id": "R-001",
                    "description": "Key developer attrition",
                    "probability": "MEDIUM",
                    "impact": "HIGH",
                    "owner": "Sarah Nguyen",
                    "status": "OPEN",
                },
            ],
            "issues": [],
            "execution": {
                "overall_percent_complete": "38",
                "earned_value": "95000",
                "planned_value": "100000",
                "actual_cost": "95000",
                "spi": "0.95",
                "cpi": "1.0",
            },
            "quality": {
                "compliance_status": "COMPLIANT",
            },
            "documents": [
                {
                    "document_type": "SOW",
                    "document_name": "Statement of Work — Acme ERP",
                    "version": "1.2",
                    "approval_status": "Approved",
                },
            ],
            "reporting": {},
            "integration": {
                "finance_accounting": "Linked to GL 4100-PRJ",
                "crm": "Opportunity OPP-2026-0142",
            },
            "closure": {},
        }
    return {"seed": True, "module": "projects", "feature": feature_code}


def _platform_extra_data(feature_code: str) -> dict:
    """Sample industry-module requirement payloads for platform demo records."""
    profiles: dict[str, dict] = {
        "business_intelligence": {
            "identity": {"example_title": "Retail Analytics Suite"},
            "industry": {
                "vertical": "Retail",
                "core_gap_rationale": "Core GL and inventory lack real-time KPI dashboards and cohort analysis.",
            },
            "features": {
                "key_features": "Real-time dashboards, drill-down KPIs, cohort analysis, predictive demand signals.",
            },
            "processes": {
                "business_processes": "Merchandising review, store performance monitoring, promotional lift analysis.",
            },
            "reporting": {
                "dashboards_kpis": "Same-store sales, basket size, inventory turns, promo ROI by SKU.",
            },
            "vendor": {
                "platform_fit": "Native PostgreSQL analytics; exports to existing Reports module.",
            },
        },
        "ecommerce": {
            "identity": {"example_title": "Omnichannel Order Hub"},
            "industry": {
                "vertical": "Retail",
                "core_gap_rationale": "Sales module lacks multi-channel inventory sync and marketplace connectors.",
            },
            "features": {
                "key_features": "Shopify/Amazon sync, unified order queue, returns routing, channel-specific pricing.",
            },
            "integration": {
                "erp_modules": "Inventory, Sales, Finance",
                "third_party": "Shopify, Amazon Seller Central, Stripe",
                "apis": "REST webhooks, middleware via message queue",
            },
        },
        "field_service": {
            "identity": {"example_title": "Healthcare Patient Management"},
            "industry": {
                "vertical": "Healthcare",
                "core_gap_rationale": "Standard CRM and HR cannot manage clinical workflows or HIPAA audit trails.",
            },
            "features": {
                "key_features": "Patient intake, appointment scheduling, clinical notes, billing handoff, care plans.",
            },
            "compliance": {
                "standards": "HIPAA, GDPR where applicable",
                "audit_trails": "Full PHI access logging with role-based masking",
            },
            "roles": {
                "user_roles": "Clinicians, nurses, billing coordinators, front-desk staff",
                "access_controls": "Role-based PHI access; break-glass emergency override",
            },
            "mobile": {
                "field_access": "Offline-capable mobile for home visits and bedside charting",
            },
        },
        "retail_pos": {
            "identity": {"example_title": "Multi-store POS Integration"},
            "industry": {
                "vertical": "Retail",
                "core_gap_rationale": "Standalone POS lacks centralized pricing, loyalty, and inventory reservation.",
            },
            "features": {
                "key_features": "POS Integration, loyalty programs, real-time stock lookup, end-of-day reconciliation.",
            },
            "integration": {
                "erp_modules": "Inventory, Sales, Finance",
                "third_party": "In-store payment terminals, loyalty platform",
                "apis": "POS REST API, nightly batch sync fallback",
            },
        },
        "plant_maintenance": {
            "identity": {"example_title": "Manufacturing Execution System - MES"},
            "industry": {
                "vertical": "Manufacturing",
                "core_gap_rationale": "Manufacturing module lacks shop-floor real-time tracking and OEE analytics.",
            },
            "features": {
                "key_features": "Bill of Materials (BOM), Production Scheduling, Quality Control, OEE dashboards.",
            },
            "processes": {
                "business_processes": "Shop floor control, work order dispatch, downtime capture, yield tracking.",
            },
            "data_requirements": {
                "entities": "Items, recipes, work centers, routings, lot/serial genealogy",
                "core_integrations": "Manufacturing, Inventory, Finance, Quality",
            },
            "compliance": {
                "standards": "ISO 9001, FDA 21 CFR Part 11 where applicable",
                "audit_trails": "Electronic batch records with operator sign-off",
            },
            "reporting": {
                "dashboards_kpis": "Yield analysis, OEE, scrap rate, schedule adherence",
            },
            "benefits": {
                "expected_outcomes": "Reduced production downtime, improved inventory accuracy",
                "roi_kpis": "OEE +8%, scrap -12%, schedule adherence +15%",
            },
        },
        "compliance_risk": {
            "identity": {"example_title": "SOX & GDPR Compliance Tracker"},
            "industry": {
                "vertical": "Professional Services",
                "core_gap_rationale": "Finance controls lack policy attestation workflows and data-subject request tracking.",
            },
            "features": {
                "key_features": "Control testing, policy management, risk register, GDPR DSAR workflow.",
            },
            "compliance": {
                "standards": "SOX, GDPR, ISO 27001",
                "audit_trails": "Immutable audit log for control evidence and attestation history",
            },
            "risks": {
                "challenges": "Legacy policy documents, inconsistent control ownership",
                "prerequisites": "Control library baseline, RACI for process owners",
            },
        },
    }

    profile = profiles.get(feature_code, {})
    base = {
        "identity": profile.get("identity", {"example_title": "Industry Module Spec"}),
        "industry": profile.get(
            "industry",
            {
                "vertical": "Other",
                "core_gap_rationale": "Standard core modules do not cover vertical-specific workflows.",
            },
        ),
        "features": profile.get(
            "features",
            {"key_features": "Configurable workflows, industry templates, regulatory reporting."},
        ),
        "processes": profile.get(
            "processes",
            {"business_processes": "End-to-end process automation aligned to industry standards."},
        ),
        "data_requirements": profile.get(
            "data_requirements",
            {
                "entities": "Master data aligned to vertical (items, patients, projects, assets)",
                "core_integrations": "Finance, Inventory, HR, CRM as applicable",
            },
        ),
        "integration": profile.get(
            "integration",
            {
                "erp_modules": "Finance, Inventory, Manufacturing, CRM",
                "third_party": "CAD, CRM, IoT devices, e-commerce platforms",
                "apis": "REST APIs, event bus, optional ETL middleware",
            },
        ),
        "compliance": profile.get(
            "compliance",
            {
                "standards": "Industry-specific (FDA, ISO, GDPR, SOX, HACCP)",
                "audit_trails": "Built-in audit trails and compliance reporting",
            },
        ),
        "reporting": profile.get(
            "reporting",
            {"dashboards_kpis": "Industry KPI dashboards and custom report builder"},
        ),
        "roles": profile.get(
            "roles",
            {
                "user_roles": "Supervisors, technicians, analysts, compliance officers",
                "access_controls": "Role-based permissions with segregation of duties",
            },
        ),
        "customization": {
            "configuration_needs": "Workflow rules, form layouts, approval chains",
            "low_code_tools": "Form builder and workflow designer where available",
        },
        "scalability": {
            "transaction_volume": "10k+ daily transactions; 50–500 concurrent users",
            "multi_site": "Multi-site and multi-company with shared master data",
        },
        "mobile": profile.get(
            "mobile",
            {"field_access": "Mobile apps with optional offline sync for field operations"},
        ),
        "implementation": {
            "effort_estimate": "3–9 months depending on scope and integrations",
            "migration": "Legacy data mapping and phased cutover",
            "training": "Role-based training for end users and administrators",
            "go_live_dependencies": "Core ERP modules live; master data cleansed",
        },
        "costs": {
            "licensing": "Per-user or per-module annual subscription",
            "implementation": "Consulting, configuration, data migration",
            "maintenance": "Annual support and upgrade fees (~18–22% of license)",
            "infrastructure": "Cloud hosting or on-prem servers as required",
        },
        "benefits": profile.get(
            "benefits",
            {
                "expected_outcomes": "Operational efficiency, compliance readiness, faster billing",
                "roi_kpis": "Measurable KPIs defined per vertical (downtime, accuracy, cycle time)",
            },
        ),
        "risks": profile.get(
            "risks",
            {
                "challenges": "Data quality in legacy systems, user adoption, integration complexity",
                "prerequisites": "Executive sponsorship, clean master data, change management plan",
            },
        ),
        "vendor": profile.get(
            "vendor",
            {
                "platform_fit": "Compatible with base ERP stack and extension model",
                "vendor_expertise": "Proven vertical experience and implementation partners",
                "references": "Similar deployments in target industry",
            },
        ),
    }
    return base


def _demo_records() -> list[dict]:
    samples: list[dict] = []
    status_cycle = ["DRAFT", "ACTIVE", "IN_PROGRESS", "COMPLETED", "APPROVED"]
    for module in MODULE_CATALOG:
        for idx, feature in enumerate(module.features):
            ref_num = idx + 1
            status = status_cycle[idx % len(status_cycle)]
            extra_data: dict = {"seed": True, "module": module.code, "feature": feature.code}
            party_name = f"Demo party ({module.short_name})"
            title = f"{feature.name} — sample {ref_num}"
            amount = Decimal("1000.00") + Decimal(idx * 250)
            start_date = date(2026, 1, 1)
            end_date = date(2026, 12, 31) if idx % 2 == 0 else None

            if module.code == "hcm":
                extra_data = _hcm_extra_data(feature.code)
                if feature.code == "employee_records":
                    title = "Alex Rivera"
                    party_name = "Jordan Lee"
                    amount = Decimal("5500.00")
                    start_date = date(2024, 3, 15)
                    end_date = None
                elif feature.code == "payroll":
                    title = "Payroll — Apr 2026"
                    party_name = "EMP-DEMO-001"
                    amount = Decimal("5500.00")
                elif feature.code == "recruitment":
                    title = "Taylor Kim"
                elif feature.code == "training":
                    title = "Workplace Safety"
            elif module.code == "manufacturing":
                extra_data = _manufacturing_extra_data(feature.code)
                if feature.code == "production_orders":
                    title = "Batch production — Dhaka Unit 1"
                    start_date = date(2026, 2, 1)
            elif module.code == "crm":
                extra_data = _crm_extra_data(feature.code)
                if feature.code == "marketing_campaigns":
                    title = "Spring VIP outreach"
                elif feature.code == "support_tickets":
                    title = "Ticket #1001 — billing inquiry"
                elif feature.code == "customer_service":
                    title = "Warranty case — garment defect"
            elif module.code == "tms":
                extra_data = _tms_extra_data(feature.code)
                if feature.code == "shipments":
                    title = "Outbound — Acme Retail Store 12"
                    party_name = "FastFreight Logistics"
                    amount = Decimal("398.50")
                    start_date = date(2026, 5, 20)
                    end_date = date(2026, 5, 25)
                    status = "IN_TRANSIT"
            elif module.code == "projects":
                extra_data = _projects_extra_data(feature.code)
                if feature.code == "project_planning":
                    title = "Acme ERP Integration — Phase 1"
                    party_name = "Acme Retail Group"
                    amount = Decimal("250000.00")
                    start_date = date(2026, 3, 1)
                    end_date = date(2026, 9, 30)
                    status = "ACTIVE"
            elif module.code == "platform":
                extra_data = _platform_extra_data(feature.code)
                industry = extra_data.get("industry", {})
                vertical = industry.get("vertical", "Other")
                identity = extra_data.get("identity", {})
                example = identity.get("example_title", feature.name)
                title = example
                party_name = vertical
                amount = Decimal("75000.00") + Decimal(idx * 15000)
                status = "IN_REVIEW" if idx % 2 == 0 else "DRAFT"
                if feature.code == "plant_maintenance":
                    title = "Manufacturing Execution System - MES"
                    party_name = "Manufacturing"
                    status = "APPROVED"
                    amount = Decimal("185000.00")
                elif feature.code == "field_service":
                    title = "Healthcare Patient Management"
                    party_name = "Healthcare"
                    status = "IN_IMPLEMENTATION"
                    amount = Decimal("220000.00")
                elif feature.code == "compliance_risk":
                    status = "LIVE"
                    amount = Decimal("95000.00")

            samples.append(
                {
                    "module_code": module.code,
                    "feature_code": feature.code,
                    "reference": f"DEMO-{ref_num:03d}"
                    if module.code != "hcm" or feature.code != "employee_records"
                    else "EMP-DEMO-001",
                    "title": title,
                    "status": status,
                    "description": feature.description,
                    "party_name": party_name,
                    "amount": amount,
                    "quantity": (idx + 1) * 10,
                    "start_date": start_date,
                    "end_date": end_date,
                    "extra_data": extra_data,
                }
            )
    return samples


async def seed_module_records_if_empty(session: AsyncSession) -> int:
    count = (await session.execute(select(func.count()).select_from(ModuleRecord))).scalar_one()
    if count > 0:
        return 0

    created = 0
    for row in _demo_records():
        session.add(ModuleRecord(**row))
        created += 1
    await session.flush()
    return created
