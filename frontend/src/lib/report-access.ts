import { canAccessAny } from "@/lib/permissions"
import type { ReportTabId } from "@/types/report"

export type ReportTabDef = {
  id: ReportTabId
  label: string
  group: string
  anyOf: string[]
}

export const REPORT_TABS: ReportTabDef[] = [
  {
    id: "sales",
    label: "Sales",
    group: "Merchandiser",
    anyOf: ["reports.merchandiser.read", "reports.reports.read", "reports.manager.read"],
  },
  {
    id: "top-products",
    label: "Top products",
    group: "Merchandiser",
    anyOf: ["reports.merchandiser.read", "reports.reports.read", "reports.manager.read"],
  },
  {
    id: "purchase-orders",
    label: "Purchase orders",
    group: "Merchandiser",
    anyOf: ["reports.merchandiser.read", "reports.reports.read", "reports.manager.read"],
  },
  {
    id: "inventory-performance",
    label: "Inventory health",
    group: "Warehouse",
    anyOf: [
      "reports.warehouse.read",
      "reports.merchandiser.read",
      "reports.reports.read",
      "reports.manager.read",
    ],
  },
  {
    id: "stock-value",
    label: "Stock value",
    group: "Warehouse",
    anyOf: [
      "reports.warehouse.read",
      "reports.merchandiser.read",
      "reports.reports.read",
      "reports.manager.read",
    ],
  },
  {
    id: "finance-summary",
    label: "Finance summary",
    group: "Finance",
    anyOf: ["reports.finance.read", "reports.reports.read", "reports.manager.read"],
  },
  {
    id: "marketing-funnel",
    label: "Marketing funnel",
    group: "Marketing",
    anyOf: ["reports.marketing.read", "reports.reports.read", "reports.manager.read"],
  },
  {
    id: "it-overview",
    label: "IT overview",
    group: "IT",
    anyOf: ["reports.it.read", "reports.reports.read", "reports.manager.read"],
  },
]

export function visibleReportTabs(permissions: string[]): ReportTabDef[] {
  return REPORT_TABS.filter((tab) => canAccessAny(permissions, tab.anyOf))
}

export function canViewAnyReport(permissions: string[]): boolean {
  return visibleReportTabs(permissions).length > 0
}

export function canViewManagerOverview(permissions: string[]): boolean {
  return canAccessAny(permissions, ["reports.manager.read", "reports.dashboard.read"])
}
