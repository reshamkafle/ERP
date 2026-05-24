import {
  BarChart3,
  Boxes,
  Briefcase,
  Building2,
  Factory,
  Handshake,
  Landmark,
  LineChart,
  Package,
  Percent,
  ShoppingCart,
  ShoppingBag,
  Truck,
  Users,
  Warehouse,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

/** Apps shown on the Odoo-style home dashboard (manager/admin). */
export type ErpApp = {
  label: string
  to: string
  slug: string
  icon: LucideIcon
  /** Tailwind classes for the icon tile background and icon color */
  tileClass: string
  iconClass: string
}

export const DASHBOARD_APPS: ErpApp[] = [
  {
    label: "Finance",
    to: "/finance",
    slug: "finance",
    icon: Landmark,
    tileClass: "bg-[#2C3E50]",
    iconClass: "text-white",
  },
  {
    label: "HCM / HR",
    to: "/hcm",
    slug: "hcm",
    icon: Users,
    tileClass: "bg-[#8E44AD]",
    iconClass: "text-white",
  },
  {
    label: "Procurement",
    to: "/procurement",
    slug: "procurement",
    icon: Truck,
    tileClass: "bg-[#3498DB]",
    iconClass: "text-white",
  },
  {
    label: "Warehouse",
    to: "/warehouse",
    slug: "warehouse",
    icon: Package,
    tileClass: "bg-[#E67E22]",
    iconClass: "text-white",
  },
  {
    label: "SCM",
    to: "/scm",
    slug: "scm",
    icon: LineChart,
    tileClass: "bg-[#16A085]",
    iconClass: "text-white",
  },
  {
    label: "TMS",
    to: "/tms",
    slug: "tms",
    icon: Truck,
    tileClass: "bg-[#2980B9]",
    iconClass: "text-white",
  },
  {
    label: "Manufacturing",
    to: "/manufacturing",
    slug: "manufacturing",
    icon: Factory,
    tileClass: "bg-[#7F8C8D]",
    iconClass: "text-white",
  },
  {
    label: "Sales & Dist.",
    to: "/sales-distribution",
    slug: "sales-dist",
    icon: ShoppingBag,
    tileClass: "bg-[#27AE60]",
    iconClass: "text-white",
  },
  {
    label: "CRM",
    to: "/crm",
    slug: "crm",
    icon: Handshake,
    tileClass: "bg-[#017E84]",
    iconClass: "text-white",
  },
  {
    label: "Projects",
    to: "/projects",
    slug: "projects",
    icon: Briefcase,
    tileClass: "bg-[#C0392B]",
    iconClass: "text-white",
  },
  {
    label: "Platform",
    to: "/platform",
    slug: "platform",
    icon: Building2,
    tileClass: "bg-[#714B67]",
    iconClass: "text-white",
  },
  {
    label: "Reports",
    to: "/reports",
    slug: "reports",
    icon: BarChart3,
    tileClass: "bg-[#714B67]",
    iconClass: "text-white",
  },
  {
    label: "Inventory",
    to: "/inventory",
    slug: "inventory",
    icon: Package,
    tileClass: "bg-[#E67E22]",
    iconClass: "text-white",
  },
  {
    label: "BOM",
    to: "/bom",
    slug: "bom",
    icon: Boxes,
    tileClass: "bg-[#8E44AD]",
    iconClass: "text-white",
  },
  {
    label: "Customers",
    to: "/customers",
    slug: "customers",
    icon: Users,
    tileClass: "bg-[#017E84]",
    iconClass: "text-white",
  },
  {
    label: "Point of Sale",
    to: "/pos",
    slug: "pos",
    icon: ShoppingCart,
    tileClass: "bg-[#27AE60]",
    iconClass: "text-white",
  },
  {
    label: "Suppliers",
    to: "/suppliers",
    slug: "suppliers",
    icon: Truck,
    tileClass: "bg-[#3498DB]",
    iconClass: "text-white",
  },
  {
    label: "Purchases",
    to: "/purchases",
    slug: "purchases",
    icon: Warehouse,
    tileClass: "bg-[#C0392B]",
    iconClass: "text-white",
  },
  {
    label: "Promotions",
    to: "/promotions",
    slug: "promotions",
    icon: Percent,
    tileClass: "bg-[#9B59B6]",
    iconClass: "text-white",
  },
]
