import type { LucideIcon } from "lucide-react"
import {
  Boxes,
  Building2,
  CalendarClock,
  ClipboardList,
  Factory,
  FileInput,
  ListTree,
  Package,
  PackageCheck,
  Receipt,
  ShieldCheck,
  ShoppingCart,
  Truck,
  Users,
} from "lucide-react"

import { canAccess, canAccessAny } from "@/lib/permissions"

export type FlowSection = "sales" | "procurement" | "production" | "finance"

export type DocumentFlowCardDef = {
  id: string
  label: string
  icon: LucideIcon
  section: FlowSection
  /** Single read permission or any-of list */
  readPermission: string | string[]
  route: string
  laneId: string
  laneTitle: string
  laneSection: FlowSection
}

export const DOCUMENT_FLOW_CARDS: DocumentFlowCardDef[] = [
  {
    id: "customer-start",
    label: "Customer",
    icon: Users,
    section: "sales",
    readPermission: "sales.customers.read",
    route: "/customers",
    laneId: "sales",
    laneTitle: "Sales & Demand",
    laneSection: "sales",
  },
  {
    id: "sales-order",
    label: "Sales Order",
    icon: ShoppingCart,
    section: "sales",
    readPermission: "sales.orders.read",
    route: "/sales",
    laneId: "sales",
    laneTitle: "Sales & Demand",
    laneSection: "sales",
  },
  {
    id: "mrp",
    label: "Production Planning / MRP",
    icon: CalendarClock,
    section: "sales",
    readPermission: "manufacturing.planning.read",
    route: "/manufacturing?feature=capacity_planning",
    laneId: "sales",
    laneTitle: "Sales & Demand",
    laneSection: "sales",
  },
  {
    id: "pr",
    label: "Purchase Requisition",
    icon: ClipboardList,
    section: "procurement",
    readPermission: "procurement.records.read",
    route: "/procurement?feature=purchase_requisitions",
    laneId: "procurement",
    laneTitle: "Procurement & Inbound",
    laneSection: "procurement",
  },
  {
    id: "po",
    label: "Purchase Order",
    icon: FileInput,
    section: "procurement",
    readPermission: "warehouse.purchases.read",
    route: "/purchases",
    laneId: "procurement",
    laneTitle: "Procurement & Inbound",
    laneSection: "procurement",
  },
  {
    id: "supplier",
    label: "Supplier",
    icon: Building2,
    section: "procurement",
    readPermission: "warehouse.suppliers.read",
    route: "/suppliers",
    laneId: "procurement",
    laneTitle: "Procurement & Inbound",
    laneSection: "procurement",
  },
  {
    id: "grn",
    label: "Goods Receipt Note",
    icon: PackageCheck,
    section: "procurement",
    readPermission: "procurement.records.read",
    route: "/procurement?feature=goods_receipt",
    laneId: "procurement",
    laneTitle: "Procurement & Inbound",
    laneSection: "procurement",
  },
  {
    id: "raw-inv",
    label: "Raw Material Inventory",
    icon: Boxes,
    section: "procurement",
    readPermission: "warehouse.inventory.read",
    route: "/inventory?item_type=RAW",
    laneId: "procurement",
    laneTitle: "Procurement & Inbound",
    laneSection: "procurement",
  },
  {
    id: "fabric-rolls",
    label: "Fabric Rolls / Lots",
    icon: Package,
    section: "procurement",
    readPermission: "warehouse.material_rolls.read",
    route: "/inventory/fabric-rolls",
    laneId: "procurement",
    laneTitle: "Procurement & Inbound",
    laneSection: "procurement",
  },
  {
    id: "bom-wo",
    label: "Bill of Materials + Work Order",
    icon: ListTree,
    section: "production",
    readPermission: ["warehouse.bom.read", "manufacturing.ops.read"],
    route: "/manufacturing",
    laneId: "production",
    laneTitle: "Manufacturing",
    laneSection: "production",
  },
  {
    id: "mfg",
    label: "Manufacturing",
    icon: Factory,
    section: "production",
    readPermission: "manufacturing.ops.read",
    route: "/manufacturing",
    laneId: "production",
    laneTitle: "Manufacturing",
    laneSection: "production",
  },
  {
    id: "qc",
    label: "Quality Inspection",
    icon: ShieldCheck,
    section: "production",
    readPermission: "manufacturing.quality.read",
    route: "/manufacturing?feature=quality_management",
    laneId: "production",
    laneTitle: "Manufacturing",
    laneSection: "production",
  },
  {
    id: "fg-inv",
    label: "Finished Goods Inventory",
    icon: Package,
    section: "production",
    readPermission: "warehouse.inventory.read",
    route: "/inventory?item_type=FINISHED",
    laneId: "production",
    laneTitle: "Manufacturing",
    laneSection: "production",
  },
  {
    id: "fg-out",
    label: "Finished Goods",
    icon: Package,
    section: "production",
    readPermission: "warehouse.inventory.read",
    route: "/inventory?item_type=FINISHED",
    laneId: "fulfillment",
    laneTitle: "Fulfillment & Billing",
    laneSection: "finance",
  },
  {
    id: "do",
    label: "Delivery Order",
    icon: Truck,
    section: "sales",
    readPermission: "sales.orders.read",
    route: "/sales?delivery_filter=open",
    laneId: "fulfillment",
    laneTitle: "Fulfillment & Billing",
    laneSection: "finance",
  },
  {
    id: "invoice",
    label: "Sales Invoice",
    icon: Receipt,
    section: "finance",
    readPermission: ["finance.payments.read", "finance.records.read"],
    route: "/finance",
    laneId: "fulfillment",
    laneTitle: "Fulfillment & Billing",
    laneSection: "finance",
  },
  {
    id: "customer-end",
    label: "Customer",
    icon: Users,
    section: "sales",
    readPermission: "sales.customers.read",
    route: "/customers",
    laneId: "fulfillment",
    laneTitle: "Fulfillment & Billing",
    laneSection: "finance",
  },
]

export const DOCUMENT_FLOW_CARD_BY_ID = Object.fromEntries(
  DOCUMENT_FLOW_CARDS.map((c) => [c.id, c]),
) as Record<string, DocumentFlowCardDef>

export const FLOW_LANE_ORDER = ["sales", "procurement", "production", "fulfillment"] as const

export type FlowLaneView = {
  id: string
  title: string
  section: FlowSection
  cards: DocumentFlowCardDef[]
}

export function canReadFlowCard(permissions: string[], card: DocumentFlowCardDef): boolean {
  if (Array.isArray(card.readPermission)) {
    return canAccessAny(permissions, card.readPermission)
  }
  return canAccess(permissions, card.readPermission)
}

export function buildVisibleFlowLanes(permissions: string[]): FlowLaneView[] {
  const visible = DOCUMENT_FLOW_CARDS.filter((c) => canReadFlowCard(permissions, c))
  return FLOW_LANE_ORDER.map((laneId) => {
    const cards = visible.filter((c) => c.laneId === laneId)
    if (cards.length === 0) return null
    return {
      id: laneId,
      title: cards[0].laneTitle,
      section: cards[0].laneSection,
      cards,
    }
  }).filter((lane): lane is FlowLaneView => lane !== null)
}

export const CROSS_LINKS: { from: string; to: string; label: string }[] = [
  { from: "mrp", to: "pr", label: "Material demand" },
  { from: "mrp", to: "bom-wo", label: "Production plan" },
  { from: "raw-inv", to: "mfg", label: "Issue materials" },
  { from: "fg-inv", to: "fg-out", label: "Available stock" },
]

export const NODE_LABELS = Object.fromEntries(
  DOCUMENT_FLOW_CARDS.map((c) => [c.id, c.label]),
) as Record<string, string>
