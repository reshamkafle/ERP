import {
  BarChart3,
  Briefcase,
  Building2,
  Factory,
  Handshake,
  Landmark,
  LineChart,
  Package,
  PackageCheck,
  ShoppingCart,
  Truck,
  Users,
  Wrench,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

export type ModuleMeta = {
  code: string
  icon: LucideIcon
  tileClass: string
  iconClass: string
}

export const MODULE_META: Record<string, ModuleMeta> = {
  finance: {
    code: "finance",
    icon: Landmark,
    tileClass: "bg-[#2C3E50]",
    iconClass: "text-white",
  },
  hcm: {
    code: "hcm",
    icon: Users,
    tileClass: "bg-[#8E44AD]",
    iconClass: "text-white",
  },
  procurement: {
    code: "procurement",
    icon: Truck,
    tileClass: "bg-[#3498DB]",
    iconClass: "text-white",
  },
  warehouse: {
    code: "warehouse",
    icon: Package,
    tileClass: "bg-[#E67E22]",
    iconClass: "text-white",
  },
  scm: {
    code: "scm",
    icon: LineChart,
    tileClass: "bg-[#16A085]",
    iconClass: "text-white",
  },
  tms: {
    code: "tms",
    icon: PackageCheck,
    tileClass: "bg-[#2980B9]",
    iconClass: "text-white",
  },
  manufacturing: {
    code: "manufacturing",
    icon: Factory,
    tileClass: "bg-[#7F8C8D]",
    iconClass: "text-white",
  },
  sales: {
    code: "sales",
    icon: ShoppingCart,
    tileClass: "bg-[#27AE60]",
    iconClass: "text-white",
  },
  crm: {
    code: "crm",
    icon: Handshake,
    tileClass: "bg-[#017E84]",
    iconClass: "text-white",
  },
  projects: {
    code: "projects",
    icon: Briefcase,
    tileClass: "bg-[#C0392B]",
    iconClass: "text-white",
  },
  platform: {
    code: "platform",
    icon: Building2,
    tileClass: "bg-[#714B67]",
    iconClass: "text-white",
  },
}

export const MODULE_ROUTE_BY_CODE: Record<string, string> = {
  finance: "/finance",
  hcm: "/hcm",
  procurement: "/procurement",
  warehouse: "/warehouse",
  scm: "/scm",
  tms: "/tms",
  manufacturing: "/manufacturing",
  sales: "/sales-distribution",
  crm: "/crm",
  projects: "/projects",
  platform: "/platform",
}

export const MODULE_CODE_BY_ROUTE: Record<string, string> = Object.fromEntries(
  Object.entries(MODULE_ROUTE_BY_CODE).map(([code, route]) => [route, code]),
)

export function moduleIcon(code: string): LucideIcon {
  return MODULE_META[code]?.icon ?? Wrench
}

export function moduleTile(code: string) {
  return (
    MODULE_META[code] ?? {
      code,
      icon: BarChart3,
      tileClass: "bg-[#5D6D7E]",
      iconClass: "text-white",
    }
  )
}
