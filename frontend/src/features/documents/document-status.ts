import type { ErpDocumentStatus } from "@/types/erp-document"

export function documentStatusVariant(status: ErpDocumentStatus) {
  switch (status) {
    case "CONFIRMED":
      return "success" as const
    case "ISSUED":
      return "default" as const
    case "CANCELLED":
      return "danger" as const
    default:
      return "secondary" as const
  }
}
