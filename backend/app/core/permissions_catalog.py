"""Permission catalog and legacy role fallbacks during migration."""

from dataclasses import dataclass

from app.models.user import UserRole


@dataclass(frozen=True)
class PermissionDef:
    code: str
    name: str
    module: str
    description: str = ""


PERMISSION_CATALOG: list[PermissionDef] = [
    # System
    PermissionDef("system.roles.manage", "Manage roles", "system", "Create roles and assign permissions"),
    PermissionDef("system.users.read", "View users", "system", "View users, roles, and effective permissions"),
    PermissionDef("system.users.manage", "Manage users", "system", "Assign roles to users"),
    # Profile
    PermissionDef(
        "profile.layout.configure",
        "Configure layout",
        "profile",
        "Customize sidebar, theme, and shell layout",
    ),
    # Reports
    PermissionDef("reports.dashboard.read", "View dashboard", "reports"),
    PermissionDef("reports.reports.read", "View all reports", "reports"),
    PermissionDef("reports.merchandiser.read", "View merchandiser reports", "reports"),
    PermissionDef("reports.finance.read", "View finance reports", "reports"),
    PermissionDef("reports.marketing.read", "View marketing reports", "reports"),
    PermissionDef("reports.warehouse.read", "View warehouse reports", "reports"),
    PermissionDef("reports.it.read", "View IT reports", "reports"),
    PermissionDef("reports.manager.read", "View manager reports", "reports"),
    # Accounting (legacy) + Finance module
    PermissionDef("accounting.records.read", "View financial records", "accounting"),
    PermissionDef("accounting.records.write", "Edit financial records", "accounting"),
    PermissionDef("finance.records.read", "View finance module", "finance"),
    PermissionDef("finance.records.write", "Manage finance module", "finance"),
    PermissionDef("finance.tax.read", "View tax rates", "finance"),
    PermissionDef("finance.tax.write", "Manage tax rates", "finance"),
    PermissionDef("finance.payments.read", "View payments", "finance"),
    PermissionDef("finance.payments.write", "Create and edit payments", "finance"),
    PermissionDef("finance.payments.approve", "Confirm and cancel payments", "finance"),
    PermissionDef("finance.gl.read", "View chart of accounts", "finance"),
    PermissionDef("hcm.records.read", "View HCM module", "hcm"),
    PermissionDef("hcm.records.write", "Manage HCM module", "hcm"),
    PermissionDef("procurement.records.read", "View procurement module", "procurement"),
    PermissionDef("procurement.records.write", "Manage procurement module", "procurement"),
    PermissionDef("warehouse.ops.read", "View warehouse operations", "warehouse"),
    PermissionDef("warehouse.ops.write", "Manage warehouse operations", "warehouse"),
    PermissionDef("scm.records.read", "View SCM module", "scm"),
    PermissionDef("scm.records.write", "Manage SCM module", "scm"),
    PermissionDef("tms.records.read", "View TMS module", "tms"),
    PermissionDef("tms.records.write", "Manage TMS module", "tms"),
    PermissionDef("manufacturing.ops.read", "View manufacturing operations", "manufacturing"),
    PermissionDef("manufacturing.ops.write", "Manage manufacturing operations", "manufacturing"),
    PermissionDef("manufacturing.master.read", "View manufacturing master data", "manufacturing"),
    PermissionDef("manufacturing.master.write", "Manage manufacturing master data", "manufacturing"),
    PermissionDef("manufacturing.planning.read", "View MRP and capacity planning", "manufacturing"),
    PermissionDef("manufacturing.planning.write", "Run MRP and capacity planning", "manufacturing"),
    PermissionDef("manufacturing.execution.read", "View shop floor execution", "manufacturing"),
    PermissionDef("manufacturing.execution.write", "Execute production orders", "manufacturing"),
    PermissionDef("manufacturing.quality.read", "View quality inspections", "manufacturing"),
    PermissionDef("manufacturing.quality.write", "Manage quality inspections", "manufacturing"),
    PermissionDef("manufacturing.costing.read", "View production costing", "manufacturing"),
    PermissionDef("sales.dist.read", "View sales & distribution", "sales"),
    PermissionDef("sales.dist.write", "Manage sales & distribution", "sales"),
    PermissionDef("crm.records.read", "View CRM module", "crm"),
    PermissionDef("crm.records.write", "Manage CRM module", "crm"),
    PermissionDef("crm.leads.read", "View CRM leads", "crm"),
    PermissionDef("crm.leads.write", "Manage CRM leads", "crm"),
    PermissionDef("crm.opportunities.read", "View CRM opportunities", "crm"),
    PermissionDef("crm.opportunities.write", "Manage CRM opportunities", "crm"),
    PermissionDef("crm.contacts.read", "View customer contacts", "crm"),
    PermissionDef("crm.contacts.write", "Manage customer contacts", "crm"),
    PermissionDef("crm.activities.read", "View CRM activities", "crm"),
    PermissionDef("crm.activities.write", "Manage CRM activities", "crm"),
    PermissionDef("projects.records.read", "View projects module", "projects"),
    PermissionDef("projects.records.write", "Manage projects module", "projects"),
    PermissionDef("platform.records.read", "View platform & industry modules", "platform"),
    PermissionDef("platform.records.write", "Manage platform & industry modules", "platform"),
    # Warehouse
    PermissionDef("warehouse.inventory.read", "View inventory", "warehouse"),
    PermissionDef("warehouse.inventory.write", "Manage inventory", "warehouse"),
    PermissionDef("warehouse.inventory.delete", "Delete inventory items", "warehouse"),
    PermissionDef("warehouse.material_rolls.read", "View fabric rolls / lots", "warehouse"),
    PermissionDef("warehouse.material_rolls.write", "Manage fabric rolls / lots", "warehouse"),
    PermissionDef("warehouse.bom.read", "View BOM", "warehouse"),
    PermissionDef("warehouse.bom.write", "Manage BOM", "warehouse"),
    PermissionDef("warehouse.purchases.read", "View purchases", "warehouse"),
    PermissionDef("warehouse.purchases.write", "Manage purchases", "warehouse"),
    PermissionDef("warehouse.purchases.delete", "Discard draft purchases", "warehouse"),
    PermissionDef("warehouse.procurement.manage", "Run procurement AI", "warehouse"),
    PermissionDef("warehouse.documents.read", "View documents", "warehouse"),
    PermissionDef("warehouse.documents.write", "Manage documents", "warehouse"),
    PermissionDef("warehouse.documents.delete", "Delete documents", "warehouse"),
    # Sales
    PermissionDef("sales.customers.read", "View customers", "sales"),
    PermissionDef("sales.customers.write", "Manage customers", "sales"),
    PermissionDef("sales.customers.delete", "Delete customers", "sales"),
    PermissionDef("sales.orders.read", "View sales", "sales"),
    PermissionDef("sales.orders.write", "Manage sales", "sales"),
    PermissionDef(
        "sales.orders.price_override",
        "Override line unit prices",
        "sales",
        "Set sale line prices different from the product catalog",
    ),
    PermissionDef("sales.pos.use", "Use POS", "sales"),
    PermissionDef("sales.promotions.manage", "Manage promotions", "sales"),
    # Suppliers
    PermissionDef("warehouse.suppliers.read", "View suppliers", "warehouse"),
    PermissionDef("warehouse.suppliers.write", "Manage suppliers", "warehouse"),
    PermissionDef("warehouse.suppliers.delete", "Delete suppliers", "warehouse"),
]

ALL_PERMISSION_CODES: frozenset[str] = frozenset(p.code for p in PERMISSION_CATALOG)

# Legacy enum → permission codes (used when user has no role_assignments yet)
_LEGACY_ADMIN: frozenset[str] = ALL_PERMISSION_CODES

_CRM_PERMISSIONS: frozenset[str] = frozenset(
    {
        "crm.records.read",
        "crm.records.write",
        "crm.leads.read",
        "crm.leads.write",
        "crm.opportunities.read",
        "crm.opportunities.write",
        "crm.contacts.read",
        "crm.contacts.write",
        "crm.activities.read",
        "crm.activities.write",
    }
)

_LEGACY_MANAGER: frozenset[str] = frozenset(
    p.code
    for p in PERMISSION_CATALOG
    if not p.code.startswith("system.") and not p.code.endswith(".delete")
) | _CRM_PERMISSIONS

_LEGACY_CASHIER: frozenset[str] = frozenset(
    {
        "sales.pos.use",
        "sales.orders.read",
        "sales.orders.write",
        "sales.customers.read",
    }
)

LEGACY_ROLE_PERMISSIONS: dict[UserRole, frozenset[str]] = {
    UserRole.ADMIN: _LEGACY_ADMIN,
    UserRole.MANAGER: _LEGACY_MANAGER,
    UserRole.CASHIER: _LEGACY_CASHIER,
}

# System role seed definitions
SYSTEM_ROLES: list[dict] = [
    {
        "name": "Super Admin",
        "role_type": "SUPER_ADMIN",
        "department": "general",
        "is_system": True,
        "permission_codes": list(ALL_PERMISSION_CODES),
        "legacy_role": UserRole.ADMIN,
    },
    {
        "name": "Manager",
        "role_type": "DIRECTOR",
        "department": "general",
        "is_system": True,
        "permission_codes": list(_LEGACY_MANAGER),
        "legacy_role": UserRole.MANAGER,
    },
    {
        "name": "Cashier",
        "role_type": "EMPLOYEE",
        "department": "sales",
        "is_system": True,
        "permission_codes": list(_LEGACY_CASHIER),
        "legacy_role": UserRole.CASHIER,
    },
    {
        "name": "Accounting",
        "role_type": "EMPLOYEE",
        "department": "accounting",
        "is_system": True,
        "permission_codes": [
            "accounting.records.read",
            "accounting.records.write",
            "finance.records.read",
            "finance.records.write",
            "finance.tax.read",
            "finance.tax.write",
            "finance.payments.read",
            "finance.payments.write",
            "finance.payments.approve",
            "finance.gl.read",
            "reports.reports.read",
            "reports.finance.read",
            "reports.dashboard.read",
            "platform.records.read",
        ],
        "legacy_role": None,
    },
    {
        "name": "Warehouse",
        "role_type": "EMPLOYEE",
        "department": "warehouse",
        "is_system": True,
        "permission_codes": [
            "warehouse.inventory.read",
            "warehouse.inventory.write",
            "warehouse.material_rolls.read",
            "warehouse.material_rolls.write",
            "warehouse.bom.read",
            "warehouse.bom.write",
            "warehouse.purchases.read",
            "warehouse.purchases.write",
            "warehouse.suppliers.read",
            "warehouse.suppliers.write",
            "warehouse.documents.read",
            "warehouse.documents.write",
            "reports.warehouse.read",
            "reports.dashboard.read",
        ],
        "legacy_role": None,
    },
    {
        "name": "Merchandiser",
        "role_type": "EMPLOYEE",
        "department": "sales",
        "is_system": True,
        "permission_codes": [
            "sales.orders.read",
            "sales.customers.read",
            "warehouse.inventory.read",
            "warehouse.purchases.read",
            "warehouse.suppliers.read",
            "reports.merchandiser.read",
            "reports.dashboard.read",
            "crm.records.read",
        ],
        "legacy_role": None,
    },
    {
        "name": "Marketing",
        "role_type": "EMPLOYEE",
        "department": "sales",
        "is_system": True,
        "permission_codes": [
            "crm.records.read",
            "crm.records.write",
            "crm.leads.read",
            "crm.leads.write",
            "crm.opportunities.read",
            "crm.opportunities.write",
            "crm.contacts.read",
            "crm.contacts.write",
            "crm.activities.read",
            "crm.activities.write",
            "sales.customers.read",
            "sales.promotions.manage",
            "reports.marketing.read",
            "reports.dashboard.read",
        ],
        "legacy_role": None,
    },
    {
        "name": "IT",
        "role_type": "IT",
        "department": "it",
        "is_system": True,
        "permission_codes": [
            "system.roles.manage",
            "system.users.read",
            "system.users.manage",
            "profile.layout.configure",
            "reports.it.read",
            "reports.dashboard.read",
            "platform.records.read",
        ],
        "legacy_role": None,
    },
]
