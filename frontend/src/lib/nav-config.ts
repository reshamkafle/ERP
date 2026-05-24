import {
  BarChart3,
  Boxes,
  Briefcase,
  Building2,
  Factory,
  Handshake,
  Landmark,
  LayoutDashboard,
  LayoutGrid,
  LineChart,
  Package,
  Percent,
  Settings,
  ShoppingBag,
  ShoppingCart,
  Truck,
  Users,
  Warehouse,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

import { canAccess, canAccessAny } from "@/lib/permissions"

export type NavItem = {
  label: string
  to: string
  slug: string
  icon: LucideIcon
  permission: string
  anyOf?: string[]
}

export type NavGroup = {
  title: string
  items: NavItem[]
}

export const NAV_GROUPS: NavGroup[] = [
  {
    title: "Overview",
    items: [
      {
        label: "Dashboard",
        to: "/dashboard",
        slug: "dashboard",
        icon: LayoutDashboard,
        permission: "reports.dashboard.read",
      },
      {
        label: "ERP Modules",
        to: "/modules",
        slug: "modules",
        icon: LayoutGrid,
        permission: "reports.dashboard.read",
      },
      {
        label: "Reports",
        to: "/reports",
        slug: "reports",
        icon: BarChart3,
        permission: "",
        anyOf: [
          "reports.reports.read",
          "reports.merchandiser.read",
          "reports.finance.read",
          "reports.marketing.read",
          "reports.warehouse.read",
          "reports.it.read",
          "reports.manager.read",
        ],
      },
    ],
  },
  {
    title: "Financial Management (FI/CO)",
    items: [
      {
        label: "Finance",
        to: "/finance",
        slug: "finance",
        icon: Landmark,
        permission: "finance.records.read",
      },
    ],
  },
  {
    title: "Human Capital (HCM)",
    items: [
      {
        label: "HCM / HR",
        to: "/hcm",
        slug: "hcm",
        icon: Users,
        permission: "hcm.records.read",
      },
    ],
  },
  {
    title: "Procurement",
    items: [
      {
        label: "Procurement",
        to: "/procurement",
        slug: "procurement",
        icon: Truck,
        permission: "procurement.records.read",
      },
      {
        label: "Suppliers",
        to: "/suppliers",
        slug: "suppliers",
        icon: Truck,
        permission: "warehouse.suppliers.read",
      },
      {
        label: "Purchases",
        to: "/purchases",
        slug: "purchases",
        icon: Warehouse,
        permission: "warehouse.purchases.read",
      },
    ],
  },
  {
    title: "Inventory & Warehouse",
    items: [
      {
        label: "Warehouses",
        to: "/warehouses",
        slug: "warehouses",
        icon: Warehouse,
        permission: "warehouse.ops.read",
      },
      {
        label: "Locations",
        to: "/locations",
        slug: "locations",
        icon: Package,
        permission: "warehouse.ops.read",
      },
      {
        label: "Inventory",
        to: "/inventory",
        slug: "inventory",
        icon: Package,
        permission: "warehouse.inventory.read",
      },
      {
        label: "Variant matrix",
        to: "/inventory/variants",
        slug: "inventory-variants",
        icon: Package,
        permission: "warehouse.inventory.read",
      },
      {
        label: "Fabric rolls",
        to: "/inventory/fabric-rolls",
        slug: "fabric-rolls",
        icon: Package,
        permission: "warehouse.material_rolls.read",
      },
      {
        label: "BOM",
        to: "/bom",
        slug: "bom",
        icon: Boxes,
        permission: "warehouse.bom.read",
      },
    ],
  },
  {
    title: "Supply Chain (SCM)",
    items: [
      {
        label: "SCM",
        to: "/scm",
        slug: "scm",
        icon: LineChart,
        permission: "scm.records.read",
      },
      {
        label: "TMS",
        to: "/tms",
        slug: "tms",
        icon: Truck,
        permission: "tms.records.read",
      },
    ],
  },
  {
    title: "Manufacturing",
    items: [
      {
        label: "Manufacturing",
        to: "/manufacturing",
        slug: "manufacturing",
        icon: Factory,
        permission: "manufacturing.ops.read",
      },
      {
        label: "Production Planning",
        to: "/manufacturing/planning",
        slug: "manufacturing-planning",
        icon: Factory,
        permission: "manufacturing.planning.read",
      },
    ],
  },
  {
    title: "Sales & CRM",
    items: [
      {
        label: "Sales & Distribution",
        to: "/sales-distribution",
        slug: "sales-distribution",
        icon: ShoppingBag,
        permission: "sales.dist.read",
      },
      {
        label: "CRM",
        to: "/crm",
        slug: "crm",
        icon: Handshake,
        permission: "crm.records.read",
      },
      {
        label: "Customers",
        to: "/customers",
        slug: "customers",
        icon: Users,
        permission: "sales.customers.read",
      },
      {
        label: "Sales",
        to: "/sales",
        slug: "sales",
        icon: ShoppingBag,
        permission: "sales.orders.read",
      },
      {
        label: "POS",
        to: "/pos",
        slug: "pos",
        icon: ShoppingCart,
        permission: "sales.pos.use",
      },
      {
        label: "Promotions",
        to: "/promotions",
        slug: "promotions",
        icon: Percent,
        permission: "sales.promotions.manage",
      },
    ],
  },
  {
    title: "Projects & Platform",
    items: [
      {
        label: "Projects",
        to: "/projects",
        slug: "projects",
        icon: Briefcase,
        permission: "projects.records.read",
      },
      {
        label: "Platform & Industry",
        to: "/platform",
        slug: "platform",
        icon: Building2,
        permission: "platform.records.read",
      },
    ],
  },
  {
    title: "Settings",
    items: [
      {
        label: "Profile",
        to: "/settings/profile",
        slug: "settings-profile",
        icon: Settings,
        permission: "",
      },
      {
        label: "Layout",
        to: "/settings/layout",
        slug: "settings-layout",
        icon: Settings,
        permission: "profile.layout.configure",
      },
      {
        label: "Access control",
        to: "/settings/access",
        slug: "settings-access",
        icon: Settings,
        permission: "system.roles.manage",
      },
      {
        label: "Users",
        to: "/settings/users",
        slug: "settings-users",
        icon: Settings,
        permission: "",
        anyOf: ["system.users.read", "system.users.manage"],
      },
    ],
  },
]

export function filterNavByPermissions(
  permissions: string[],
  hiddenSlugs: string[] = [],
): NavGroup[] {
  const hidden = new Set(hiddenSlugs)
  return NAV_GROUPS.map((group) => ({
    ...group,
    items: group.items.filter((item) => {
      if (hidden.has(item.slug)) return false
      if (item.anyOf?.length) return canAccessAny(permissions, item.anyOf)
      if (!item.permission) return true
      return canAccess(permissions, item.permission)
    }),
  })).filter((group) => group.items.length > 0)
}
