"""Manifest for 50 RBAC seed users and custom roles (dev/demo)."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.role import Department, RoleType
from app.models.user import UserRole


@dataclass(frozen=True)
class CustomRoleSpec:
    name: str
    role_type: RoleType
    permission_codes: tuple[str, ...]
    department: Department | None = None
    description: str = ""


@dataclass(frozen=True)
class SeedUserSpec:
    index: int
    slug: str
    legacy_role: UserRole
    """System role name (e.g. 'Manager') or custom role name from CUSTOM_ROLES."""
    role_name: str

    @property
    def email(self) -> str:
        return f"rbac-{self.index:02d}-{self.slug}@seed.local"


# Non-system roles created by the seed script (stable names for idempotent upsert).
CUSTOM_ROLES: tuple[CustomRoleSpec, ...] = (
    CustomRoleSpec(
        "Seed: Documents Read",
        RoleType.EMPLOYEE,
        ("warehouse.documents.read",),
        Department.WAREHOUSE,
        "View ERP documents only",
    ),
    CustomRoleSpec(
        "Seed: Documents Read Write",
        RoleType.EMPLOYEE,
        ("warehouse.documents.read", "warehouse.documents.write"),
        Department.WAREHOUSE,
        "Create and edit documents (no delete)",
    ),
    CustomRoleSpec(
        "Seed: Documents Delete Only",
        RoleType.EMPLOYEE,
        ("warehouse.documents.delete",),
        Department.WAREHOUSE,
        "Delete documents only",
    ),
    CustomRoleSpec(
        "Seed: Customer Delete",
        RoleType.EMPLOYEE,
        ("sales.customers.delete",),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: Documents Delete",
        RoleType.EMPLOYEE,
        ("warehouse.documents.delete",),
        Department.WAREHOUSE,
    ),
    CustomRoleSpec(
        "Seed: Inventory Delete",
        RoleType.EMPLOYEE,
        ("warehouse.inventory.delete",),
        Department.WAREHOUSE,
    ),
    CustomRoleSpec(
        "Seed: Purchase Delete",
        RoleType.EMPLOYEE,
        ("warehouse.purchases.delete",),
        Department.WAREHOUSE,
    ),
    CustomRoleSpec(
        "Seed: Supplier Delete",
        RoleType.EMPLOYEE,
        ("warehouse.suppliers.delete",),
        Department.WAREHOUSE,
    ),
    CustomRoleSpec(
        "Seed: Roles Manage",
        RoleType.IT,
        ("system.roles.manage",),
        Department.IT,
    ),
    CustomRoleSpec(
        "Seed: Users Manage",
        RoleType.ADMIN,
        ("system.users.manage",),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Layout Configure",
        RoleType.IT,
        ("profile.layout.configure",),
        Department.IT,
    ),
    CustomRoleSpec(
        "Seed: Price Override",
        RoleType.EMPLOYEE,
        (
            "sales.orders.price_override",
            "sales.orders.read",
            "sales.orders.write",
        ),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: Promotions Manage",
        RoleType.EMPLOYEE,
        ("sales.promotions.manage",),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: POS Focused",
        RoleType.EMPLOYEE,
        (
            "sales.pos.use",
            "sales.orders.read",
            "sales.orders.write",
            "sales.customers.read",
        ),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: Mfg Ops Read",
        RoleType.EMPLOYEE,
        ("manufacturing.ops.read",),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Mfg Master Read",
        RoleType.EMPLOYEE,
        ("manufacturing.master.read",),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Mfg Planning Read",
        RoleType.EMPLOYEE,
        ("manufacturing.planning.read",),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Mfg Execution Read",
        RoleType.EMPLOYEE,
        ("manufacturing.execution.read",),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Mfg Quality Read",
        RoleType.EMPLOYEE,
        ("manufacturing.quality.read",),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Mfg Costing Read",
        RoleType.EMPLOYEE,
        ("manufacturing.costing.read",),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: CRM Leads Read",
        RoleType.EMPLOYEE,
        ("crm.leads.read",),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: CRM Leads Write",
        RoleType.EMPLOYEE,
        ("crm.leads.read", "crm.leads.write"),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: CRM Opportunities",
        RoleType.EMPLOYEE,
        ("crm.opportunities.read", "crm.opportunities.write"),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: CRM Contacts",
        RoleType.EMPLOYEE,
        ("crm.contacts.read", "crm.contacts.write"),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: CRM Activities",
        RoleType.EMPLOYEE,
        ("crm.activities.read", "crm.activities.write"),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: CRM Records",
        RoleType.EMPLOYEE,
        ("crm.records.read", "crm.records.write"),
        Department.SALES,
    ),
    CustomRoleSpec(
        "Seed: Finance Tax",
        RoleType.EMPLOYEE,
        ("finance.tax.read", "finance.tax.write"),
        Department.ACCOUNTING,
    ),
    CustomRoleSpec(
        "Seed: Finance Payments Approve",
        RoleType.EMPLOYEE,
        (
            "finance.payments.read",
            "finance.payments.write",
            "finance.payments.approve",
        ),
        Department.ACCOUNTING,
    ),
    CustomRoleSpec(
        "Seed: Finance GL Read",
        RoleType.EMPLOYEE,
        ("finance.gl.read",),
        Department.ACCOUNTING,
    ),
    CustomRoleSpec(
        "Seed: Finance Records",
        RoleType.EMPLOYEE,
        ("finance.records.read", "finance.records.write"),
        Department.ACCOUNTING,
    ),
    CustomRoleSpec(
        "Seed: Accounting Records",
        RoleType.EMPLOYEE,
        ("accounting.records.read", "accounting.records.write"),
        Department.ACCOUNTING,
    ),
    CustomRoleSpec(
        "Seed: HCM",
        RoleType.EMPLOYEE,
        ("hcm.records.read", "hcm.records.write"),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: SCM",
        RoleType.EMPLOYEE,
        ("scm.records.read", "scm.records.write"),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: TMS",
        RoleType.EMPLOYEE,
        ("tms.records.read", "tms.records.write"),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Projects",
        RoleType.EMPLOYEE,
        ("projects.records.read", "projects.records.write"),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Platform",
        RoleType.EMPLOYEE,
        ("platform.records.read", "platform.records.write"),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Procurement Records",
        RoleType.EMPLOYEE,
        ("procurement.records.read", "procurement.records.write"),
        Department.GENERAL,
    ),
    CustomRoleSpec(
        "Seed: Procurement AI",
        RoleType.EMPLOYEE,
        ("warehouse.procurement.manage",),
        Department.WAREHOUSE,
    ),
    CustomRoleSpec(
        "Seed: Material Rolls",
        RoleType.EMPLOYEE,
        (
            "warehouse.material_rolls.read",
            "warehouse.material_rolls.write",
        ),
        Department.WAREHOUSE,
    ),
    CustomRoleSpec(
        "Seed: Inventory Write",
        RoleType.EMPLOYEE,
        ("warehouse.inventory.read", "warehouse.inventory.write"),
        Department.WAREHOUSE,
        "Inventory write without delete",
    ),
)

CUSTOM_ROLE_BY_NAME: dict[str, CustomRoleSpec] = {r.name: r for r in CUSTOM_ROLES}

# 50 users: system roles (10) + specialists (40).
SEED_USERS: tuple[SeedUserSpec, ...] = (
    # System roles ×2 each
    SeedUserSpec(1, "super-admin-a", UserRole.ADMIN, "Super Admin"),
    SeedUserSpec(2, "super-admin-b", UserRole.ADMIN, "Super Admin"),
    SeedUserSpec(3, "manager-a", UserRole.MANAGER, "Manager"),
    SeedUserSpec(4, "manager-b", UserRole.MANAGER, "Manager"),
    SeedUserSpec(5, "cashier-a", UserRole.CASHIER, "Cashier"),
    SeedUserSpec(6, "cashier-b", UserRole.CASHIER, "Cashier"),
    SeedUserSpec(7, "accounting-a", UserRole.MANAGER, "Accounting"),
    SeedUserSpec(8, "accounting-b", UserRole.MANAGER, "Accounting"),
    SeedUserSpec(9, "warehouse-a", UserRole.MANAGER, "Warehouse"),
    SeedUserSpec(10, "warehouse-b", UserRole.MANAGER, "Warehouse"),
    # Document specialists
    SeedUserSpec(11, "documents-read", UserRole.MANAGER, "Seed: Documents Read"),
    SeedUserSpec(12, "documents-write", UserRole.MANAGER, "Seed: Documents Read Write"),
    SeedUserSpec(13, "documents-delete-only", UserRole.MANAGER, "Seed: Documents Delete Only"),
    # Delete specialists
    SeedUserSpec(14, "customer-delete", UserRole.MANAGER, "Seed: Customer Delete"),
    SeedUserSpec(15, "documents-delete", UserRole.MANAGER, "Seed: Documents Delete"),
    SeedUserSpec(16, "inventory-delete", UserRole.MANAGER, "Seed: Inventory Delete"),
    SeedUserSpec(17, "purchase-delete", UserRole.MANAGER, "Seed: Purchase Delete"),
    SeedUserSpec(18, "supplier-delete", UserRole.MANAGER, "Seed: Supplier Delete"),
    # System / profile
    SeedUserSpec(19, "roles-manage", UserRole.ADMIN, "Seed: Roles Manage"),
    SeedUserSpec(20, "users-manage", UserRole.ADMIN, "Seed: Users Manage"),
    SeedUserSpec(21, "layout-configure", UserRole.MANAGER, "Seed: Layout Configure"),
    # Sales edge
    SeedUserSpec(22, "price-override", UserRole.MANAGER, "Seed: Price Override"),
    SeedUserSpec(23, "promotions-manage", UserRole.MANAGER, "Seed: Promotions Manage"),
    SeedUserSpec(24, "pos-focused", UserRole.CASHIER, "Seed: POS Focused"),
    # Manufacturing
    SeedUserSpec(25, "mfg-ops-read", UserRole.MANAGER, "Seed: Mfg Ops Read"),
    SeedUserSpec(26, "mfg-master-read", UserRole.MANAGER, "Seed: Mfg Master Read"),
    SeedUserSpec(27, "mfg-planning-read", UserRole.MANAGER, "Seed: Mfg Planning Read"),
    SeedUserSpec(28, "mfg-execution-read", UserRole.MANAGER, "Seed: Mfg Execution Read"),
    SeedUserSpec(29, "mfg-quality-read", UserRole.MANAGER, "Seed: Mfg Quality Read"),
    SeedUserSpec(30, "mfg-costing-read", UserRole.MANAGER, "Seed: Mfg Costing Read"),
    # CRM
    SeedUserSpec(31, "crm-leads-read", UserRole.MANAGER, "Seed: CRM Leads Read"),
    SeedUserSpec(32, "crm-leads-write", UserRole.MANAGER, "Seed: CRM Leads Write"),
    SeedUserSpec(33, "crm-opportunities", UserRole.MANAGER, "Seed: CRM Opportunities"),
    SeedUserSpec(34, "crm-contacts", UserRole.MANAGER, "Seed: CRM Contacts"),
    SeedUserSpec(35, "crm-activities", UserRole.MANAGER, "Seed: CRM Activities"),
    SeedUserSpec(36, "crm-records", UserRole.MANAGER, "Seed: CRM Records"),
    # Finance / accounting
    SeedUserSpec(37, "finance-tax", UserRole.MANAGER, "Seed: Finance Tax"),
    SeedUserSpec(38, "finance-payments-approve", UserRole.MANAGER, "Seed: Finance Payments Approve"),
    SeedUserSpec(39, "finance-gl-read", UserRole.MANAGER, "Seed: Finance GL Read"),
    SeedUserSpec(40, "finance-records", UserRole.MANAGER, "Seed: Finance Records"),
    SeedUserSpec(41, "accounting-records", UserRole.MANAGER, "Seed: Accounting Records"),
    # Cross-module
    SeedUserSpec(42, "hcm", UserRole.MANAGER, "Seed: HCM"),
    SeedUserSpec(43, "scm", UserRole.MANAGER, "Seed: SCM"),
    SeedUserSpec(44, "tms", UserRole.MANAGER, "Seed: TMS"),
    SeedUserSpec(45, "projects", UserRole.MANAGER, "Seed: Projects"),
    SeedUserSpec(46, "platform", UserRole.MANAGER, "Seed: Platform"),
    SeedUserSpec(47, "procurement-records", UserRole.MANAGER, "Seed: Procurement Records"),
    # Warehouse extras
    SeedUserSpec(48, "procurement-ai", UserRole.MANAGER, "Seed: Procurement AI"),
    SeedUserSpec(49, "material-rolls", UserRole.MANAGER, "Seed: Material Rolls"),
    SeedUserSpec(50, "inventory-write", UserRole.MANAGER, "Seed: Inventory Write"),
)

assert len(SEED_USERS) == 50
