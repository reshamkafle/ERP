"""ERP module and feature catalog — single source of truth for navigation and APIs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleFeature:
    code: str
    name: str
    description: str


@dataclass(frozen=True)
class ErpModuleDef:
    code: str
    name: str
    short_name: str
    description: str
    permission_read: str
    permission_write: str
    route_path: str
    features: tuple[ModuleFeature, ...]
    linked_routes: tuple[str, ...] = ()


MODULE_CATALOG: tuple[ErpModuleDef, ...] = (
    ErpModuleDef(
        code="finance",
        name="Financial Management (FI/CO)",
        short_name="Finance",
        description="General ledger, AP/AR, reporting, budgeting, assets, cost controlling, and compliance.",
        permission_read="finance.records.read",
        permission_write="finance.records.write",
        route_path="/finance",
        linked_routes=("/reports",),
        features=(
            ModuleFeature("general_ledger", "General Ledger", "Chart of accounts and journal entries"),
            ModuleFeature("accounts_payable", "Accounts Payable", "Vendor invoices and payment runs"),
            ModuleFeature("accounts_receivable", "Accounts Receivable", "Customer invoices and collections"),
            ModuleFeature("financial_reporting", "Financial Reporting", "P&L, balance sheet, and cash flow"),
            ModuleFeature("budgeting", "Budgeting & Forecasting", "Budget versions and variance analysis"),
            ModuleFeature("asset_management", "Asset Management", "Fixed assets, depreciation, and disposal"),
            ModuleFeature("cost_controlling", "Cost Controlling", "Cost centers and profitability analysis"),
            ModuleFeature("compliance_tax", "Compliance & Taxation", "Tax rules, filings, and audit trail"),
        ),
    ),
    ErpModuleDef(
        code="hcm",
        name="Human Capital Management (HCM) / HR",
        short_name="HCM / HR",
        description="Payroll, recruitment, employee lifecycle, performance, training, time, and benefits.",
        permission_read="hcm.records.read",
        permission_write="hcm.records.write",
        route_path="/hcm",
        features=(
            ModuleFeature("payroll", "Payroll Processing", "Pay runs, deductions, and payslips"),
            ModuleFeature("recruitment", "Recruitment & Onboarding", "Job postings and candidate pipeline"),
            ModuleFeature("employee_records", "Employee Records", "Core HR master data and org structure"),
            ModuleFeature("performance", "Performance Management", "Reviews, goals, and ratings"),
            ModuleFeature("training", "Training & Development", "Courses, enrollments, and certifications"),
            ModuleFeature("time_attendance", "Time & Attendance", "Clock-in/out and leave balances"),
            ModuleFeature("benefits", "Benefits Administration", "Plans, enrollments, and eligibility"),
        ),
    ),
    ErpModuleDef(
        code="procurement",
        name="Procurement / Purchasing",
        short_name="Procurement",
        description="Vendor management, requisitions, orders, contracts, and invoice matching.",
        permission_read="procurement.records.read",
        permission_write="procurement.records.write",
        route_path="/procurement",
        linked_routes=("/suppliers", "/purchases"),
        features=(
            ModuleFeature("vendor_management", "Vendor Management", "Supplier master and collaboration"),
            ModuleFeature("purchase_requisitions", "Purchase Requisitions", "Internal requests for goods/services"),
            ModuleFeature("purchase_orders", "Purchase Orders", "PO issuance and approval workflow"),
            ModuleFeature("goods_receipt", "Goods Receipt (GRN)", "Inbound delivery and quality inspection"),
            ModuleFeature("contracts", "Contracts", "Framework agreements and terms"),
            ModuleFeature("invoice_matching", "Invoice Matching", "3-way match PO–GRN–invoice"),
            ModuleFeature("payment_processing", "Payment Processing", "Payment batches and remittance"),
        ),
    ),
    ErpModuleDef(
        code="warehouse",
        name="Inventory & Warehouse Management",
        short_name="Warehouse",
        description="Real-time stock, warehouse operations, cycle counting, and optimization.",
        permission_read="warehouse.ops.read",
        permission_write="warehouse.ops.write",
        route_path="/warehouse",
        linked_routes=("/inventory",),
        features=(
            ModuleFeature("stock_tracking", "Stock Tracking", "Real-time inventory levels by location"),
            ModuleFeature("receiving", "Receiving", "Inbound ASN and put-away"),
            ModuleFeature("picking", "Picking", "Pick lists and wave planning"),
            ModuleFeature("packing", "Packing", "Pack stations and cartonization"),
            ModuleFeature("shipping", "Shipping", "Outbound shipments and carriers"),
            ModuleFeature("cycle_counting", "Cycle Counting", "Physical counts and adjustments"),
            ModuleFeature("optimization", "Inventory Optimization", "Reorder points and ABC analysis"),
        ),
    ),
    ErpModuleDef(
        code="scm",
        name="Supply Chain Management (SCM)",
        short_name="SCM",
        description="Demand planning, logistics, transportation, and supplier relationships.",
        permission_read="scm.records.read",
        permission_write="scm.records.write",
        route_path="/scm",
        linked_routes=(
            "/inventory",
            "/suppliers",
            "/warehouses",
            "/locations",
            "/bom",
            "/purchases",
            "/customers",
            "/sales",
            "/reports",
        ),
        features=(
            ModuleFeature("demand_planning", "Demand Planning", "Statistical forecasts and consensus"),
            ModuleFeature("forecasting", "Forecasting", "Seasonal and promotional uplift models"),
            ModuleFeature("logistics", "Logistics Management", "Inbound/outbound logistics coordination"),
            ModuleFeature("transportation", "Transportation", "Carriers, routes, and freight costs"),
            ModuleFeature("supplier_relationship", "Supplier Relationship", "Scorecards, audits, and SLAs"),
        ),
    ),
    ErpModuleDef(
        code="tms",
        name="Transportation Management System",
        short_name="TMS",
        description="Shipment planning, carrier rating, tracking, compliance, and freight audit.",
        permission_read="tms.records.read",
        permission_write="tms.records.write",
        route_path="/tms",
        linked_routes=("/sales", "/warehouse", "/customers", "/inventory"),
        features=(
            ModuleFeature("shipments", "Shipment Management", "Outbound and inbound shipments with full logistics detail"),
        ),
    ),
    ErpModuleDef(
        code="manufacturing",
        name="Manufacturing / Production",
        short_name="Manufacturing",
        description="BOM, routing, production orders, shop floor, quality, and order strategies.",
        permission_read="manufacturing.ops.read",
        permission_write="manufacturing.ops.write",
        route_path="/manufacturing",
        linked_routes=("/bom",),
        features=(
            ModuleFeature("bom_routing", "BOM & Routing", "Multi-level BOM and operation sequences"),
            ModuleFeature("production_orders", "Production Orders", "Planned and released manufacturing orders"),
            ModuleFeature("shop_floor", "Shop Floor Control", "Work centers, labor, and WIP tracking"),
            ModuleFeature("capacity_planning", "Capacity Planning", "Load leveling and finite scheduling"),
            ModuleFeature(
                "garment_planning",
                "Production Planning & Scheduling",
                "APS, CMT contracts, cut orders, and line balancing",
            ),
            ModuleFeature("quality_management", "Quality Management", "Inspections, NCRs, and CAPA"),
            ModuleFeature("make_to_order", "Make-to-Order", "MTO production linked to sales orders"),
            ModuleFeature("make_to_stock", "Make-to-Stock", "MTS replenishment and finished goods"),
            ModuleFeature("engineer_to_order", "Engineer-to-Order", "ETO projects with custom BOM revisions"),
        ),
    ),
    ErpModuleDef(
        code="sales",
        name="Sales & Distribution (Order Management)",
        short_name="Sales & Distribution",
        description="Quotations, pricing, order fulfillment, shipping, and returns.",
        permission_read="sales.dist.read",
        permission_write="sales.dist.write",
        route_path="/sales-distribution",
        linked_routes=("/sales", "/pos", "/promotions"),
        features=(
            ModuleFeature("quotations", "Quotations", "Sales quotes and conversion to orders"),
            ModuleFeature("pricing_promotions", "Pricing & Promotions", "Price lists, discounts, and campaigns"),
            ModuleFeature("order_processing", "Sales Order Processing", "Order entry, allocation, and status"),
            ModuleFeature("fulfillment", "Order Fulfillment", "Pick-pack-ship and delivery confirmation"),
            ModuleFeature("shipping", "Shipping", "Carriers, tracking, and proof of delivery"),
            ModuleFeature("returns_service", "Returns & After-Sales", "RMAs, repairs, and warranties"),
        ),
    ),
    ErpModuleDef(
        code="crm",
        name="Customer Relationship Management (CRM)",
        short_name="CRM",
        description="Contacts, pipeline, marketing campaigns, and customer support.",
        permission_read="crm.records.read",
        permission_write="crm.records.write",
        route_path="/crm",
        linked_routes=("/customers",),
        features=(
            ModuleFeature("contacts", "Contact Management", "Accounts, contacts, and communication history"),
            ModuleFeature("sales_pipeline", "Sales Pipeline", "Leads, opportunities, and stages"),
            ModuleFeature("marketing_campaigns", "Marketing Campaigns", "Segments, campaigns, and responses"),
            ModuleFeature("customer_service", "Customer Service", "Cases, SLAs, and knowledge base"),
            ModuleFeature("support_tickets", "Support Ticketing", "Tickets, escalations, and resolution"),
        ),
    ),
    ErpModuleDef(
        code="projects",
        name="Project Management",
        short_name="Projects",
        description="Planning, budgeting, resources, time tracking, milestones, and project billing.",
        permission_read="projects.records.read",
        permission_write="projects.records.write",
        route_path="/projects",
        features=(
            ModuleFeature("project_planning", "Project Planning", "WBS, schedules, and dependencies"),
            ModuleFeature("budgeting", "Project Budgeting", "Cost and revenue budgets by phase"),
            ModuleFeature("resource_allocation", "Resource Allocation", "People, equipment, and materials"),
            ModuleFeature("time_tracking", "Time Tracking", "Timesheets and billable hours"),
            ModuleFeature("milestones", "Milestone Monitoring", "Deliverables, gates, and status"),
            ModuleFeature("project_accounting", "Project Accounting", "WIP, billing, and revenue recognition"),
        ),
    ),
    ErpModuleDef(
        code="platform",
        name="Additional / Industry-Specific Modules",
        short_name="Platform & Industry",
        description="BI, e-commerce, field service, retail POS, plant maintenance, and compliance.",
        permission_read="platform.records.read",
        permission_write="platform.records.write",
        route_path="/platform",
        linked_routes=("/reports", "/pos"),
        features=(
            ModuleFeature("business_intelligence", "Business Intelligence", "Dashboards, KPIs, and analytics"),
            ModuleFeature("ecommerce", "E-commerce Integration", "Online channels and order sync"),
            ModuleFeature("field_service", "Service Management", "Field service orders and maintenance"),
            ModuleFeature("retail_pos", "Retail / POS", "Store POS and retail operations"),
            ModuleFeature("plant_maintenance", "Plant Maintenance", "Assets, work orders, and downtime"),
            ModuleFeature("compliance_risk", "Compliance & Risk", "GDPR, SOX, policies, and controls"),
        ),
    ),
)

MODULE_BY_CODE: dict[str, ErpModuleDef] = {m.code: m for m in MODULE_CATALOG}

ALL_MODULE_READ_PERMISSIONS: frozenset[str] = frozenset(m.permission_read for m in MODULE_CATALOG)
ALL_MODULE_WRITE_PERMISSIONS: frozenset[str] = frozenset(m.permission_write for m in MODULE_CATALOG)
