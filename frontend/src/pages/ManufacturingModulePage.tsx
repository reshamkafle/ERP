import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ExternalLink } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { ManufacturingRecordFormDialog } from "@/features/manufacturing/ManufacturingRecordFormDialog"
import { ProductionOrderFormDialog } from "@/features/manufacturing/ProductionOrderFormDialog"
import {
  fetchProductionOrders,
  type ProductionOrder,
} from "@/features/manufacturing/production-order-api"
import {
  deleteModuleRecord,
  fetchModuleOverview,
  fetchModuleRecords,
} from "@/features/modules/modules-api"
import { useAuth } from "@/context/AuthContext"
import {
  itemCodeFromRecord,
  MANUFACTURING_MODULE_CODE,
  productionStatusFromRecord,
} from "@/lib/manufacturing-record-schema"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"
import type { ModuleRecord } from "@/types/module"

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "COMPLETED" || s === "APPROVED") return "success"
  if (s === "IN_PROGRESS" || s === "ACTIVE") return "default"
  if (s === "DRAFT") return "secondary"
  if (s === "REJECTED" || s === "CANCELLED") return "danger"
  return "warning"
}

type ColumnDef = {
  key: string
  header: string
  cell: (r: ModuleRecord) => React.ReactNode
  className?: string
}

function columnsForFeature(
  _feature: string | "all",
  overviewFeatures: { code: string; name: string }[],
): ColumnDef[] {
  const featureName = (code: string) =>
    overviewFeatures.find((f) => f.code === code)?.name ?? code

  const base: ColumnDef[] = [
    {
      key: "reference",
      header: "Reference",
      cell: (r) => <span className="font-mono text-xs">{r.reference}</span>,
    },
    {
      key: "feature",
      header: "Feature",
      cell: (r) => (
        <span className="text-xs text-muted-foreground">{featureName(r.feature_code)}</span>
      ),
    },
  ]

  return [
    ...base,
    { key: "title", header: "Title", cell: (r) => r.title },
    {
      key: "item_code",
      header: "Item code",
      cell: (r) => <span className="text-xs">{itemCodeFromRecord(r)}</span>,
    },
    {
      key: "prod_status",
      header: "Prod. status",
      cell: (r) => (
        <span className="text-xs text-muted-foreground">{productionStatusFromRecord(r)}</span>
      ),
    },
    {
      key: "status",
      header: "Status",
      cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
    },
  ]
}

function productionOrderColumns(): {
  key: string
  header: string
  cell: (po: ProductionOrder) => React.ReactNode
  className?: string
}[] {
  return [
    {
      key: "order_number",
      header: "Order #",
      cell: (po) => (
        <Link
          to={`/manufacturing/orders/${po.id}`}
          className="font-mono text-xs text-primary hover:underline"
        >
          {po.order_number}
        </Link>
      ),
    },
    {
      key: "product",
      header: "Product",
      cell: (po) => (
        <span className="text-xs">
          {po.product_sku ?? po.product_id} {po.product_name ? `— ${po.product_name}` : ""}
        </span>
      ),
    },
    {
      key: "qty",
      header: "Qty planned",
      cell: (po) => po.quantity_planned,
      className: "text-right tabular-nums",
    },
    {
      key: "completed",
      header: "Completed",
      cell: (po) => po.quantity_completed,
      className: "text-right tabular-nums",
    },
    {
      key: "dates",
      header: "Schedule",
      cell: (po) => (
        <span className="text-xs text-muted-foreground">
          {po.start_date ?? "—"} → {po.end_date ?? "—"}
        </span>
      ),
    },
    {
      key: "priority",
      header: "Priority",
      cell: (po) => po.priority,
    },
    {
      key: "status",
      header: "Status",
      cell: (po) => <Badge variant={statusVariant(po.status)}>{po.status}</Badge>,
    },
  ]
}

export function ManufacturingModulePage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const featureFromUrl = searchParams.get("feature") ?? ""
  const tabFromUrl = searchParams.get("tab")
  const initialFeature =
    featureFromUrl ||
    (tabFromUrl === "mrp" ? "capacity_planning" : "") ||
    "all"
  const [activeFeature, setActiveFeature] = useState<string | "all">(initialFeature)
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [poDialogOpen, setPoDialogOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editingPoId, setEditingPoId] = useState<number | null>(null)

  useEffect(() => {
    if (featureFromUrl) {
      setActiveFeature(featureFromUrl)
    } else if (tabFromUrl === "mrp") {
      setActiveFeature("capacity_planning")
    }
  }, [featureFromUrl, tabFromUrl])

  const overviewQuery = useQuery({
    queryKey: ["erp-modules", MANUFACTURING_MODULE_CODE, "overview"],
    queryFn: () => fetchModuleOverview(MANUFACTURING_MODULE_CODE),
  })

  const showProductionOrders =
    activeFeature === "production_orders" || activeFeature === "all"

  const productionOrdersQuery = useQuery({
    queryKey: ["production-orders", search],
    queryFn: () => fetchProductionOrders({ limit: 100 }),
    enabled: showProductionOrders,
  })

  const recordsQuery = useQuery({
    queryKey: ["erp-modules", MANUFACTURING_MODULE_CODE, "records", activeFeature, search],
    queryFn: () =>
      fetchModuleRecords(MANUFACTURING_MODULE_CODE, {
        feature_code:
          activeFeature === "all" || activeFeature === "production_orders"
            ? undefined
            : activeFeature,
        search: search || undefined,
        limit: 100,
      }),
    enabled: activeFeature !== "production_orders",
  })

  const canWrite = canAccess(permissions, "manufacturing.ops.write")

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteModuleRecord(MANUFACTURING_MODULE_CODE, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", MANUFACTURING_MODULE_CODE] })
      toast.success("Record deleted")
    },
    onError: () => toast.error("Could not delete record"),
  })

  const overview = overviewQuery.data
  const records = (recordsQuery.data?.items ?? []).filter(
    (r) => r.feature_code !== "production_orders",
  )
  const productionOrders = productionOrdersQuery.data?.items ?? []
  const poColumns = productionOrderColumns()
  const features = overview?.features ?? []

  const defaultFeatureCode = useMemo(() => {
    if (activeFeature !== "all") return activeFeature
    return features.find((f) => f.code === "bom_routing")?.code ?? features[0]?.code ?? "bom_routing"
  }, [activeFeature, features])

  const columns = useMemo(
    () => columnsForFeature(activeFeature, features),
    [activeFeature, features],
  )

  const searchPlaceholder = "Search reference, title, order number…"

  const colSpan = columns.length + (canWrite ? 1 : 0)
  const poColSpan = poColumns.length + (canWrite ? 1 : 0)

  const filteredPo = productionOrders.filter((po) => {
    if (!search.trim()) return true
    const q = search.toLowerCase()
    return (
      po.order_number.toLowerCase().includes(q) ||
      (po.product_sku?.toLowerCase().includes(q) ?? false) ||
      (po.product_name?.toLowerCase().includes(q) ?? false)
    )
  })

  return (
    <div className="space-y-4">
      <PageHeader
        title={overview?.module_name ?? "Manufacturing / Production"}
        description={overview?.description}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <Link
              to="/bom"
              className="inline-flex h-8 items-center rounded-md border border-input bg-background px-3 text-xs font-medium shadow-xs hover:bg-accent hover:text-accent-foreground"
            >
              <ExternalLink className="mr-1 size-3.5" aria-hidden />
              BOM editor
            </Link>
            {canWrite ? (
              <>
                {showProductionOrders ? (
                  <Button
                    type="button"
                    data-testid="new-production-order"
                    onClick={() => {
                      setEditingPoId(null)
                      setPoDialogOpen(true)
                    }}
                  >
                    New production order
                  </Button>
                ) : null}
                {activeFeature !== "production_orders" ? (
                  <Button
                    type="button"
                    variant={showProductionOrders ? "outline" : "default"}
                    onClick={() => {
                      setEditingId(null)
                      setDialogOpen(true)
                    }}
                  >
                    Add module record
                  </Button>
                ) : null}
              </>
            ) : null}
          </div>
        }
      />

      {overview?.integration_metrics.length ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {overview.integration_metrics.map((m) => (
            <ContentSheet key={m.label} className="p-4">
              <p className="text-xs uppercase text-muted-foreground">{m.label}</p>
              <p className="mt-1 text-lg font-semibold">{m.value}</p>
              {m.hint ? <p className="mt-0.5 text-xs text-muted-foreground">{m.hint}</p> : null}
            </ContentSheet>
          ))}
        </div>
      ) : null}

      <ContentSheet className="p-4">
        <h2 className="text-sm font-semibold">Capabilities</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          {overview?.total_records ?? 0} module records across {features.length} areas. Production
          orders use operational work orders with MRP, shop floor, and costing integration.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to="/manufacturing/planning">Production Planning (APS)</Link>
          </Button>
          <button
            type="button"
            onClick={() => setActiveFeature("all")}
            className={cn(
              "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
              activeFeature === "all"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80",
            )}
          >
            All
          </button>
          {features.map((f) => (
            <button
              key={f.code}
              type="button"
              onClick={() => setActiveFeature(f.code)}
              className={cn(
                "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                activeFeature === f.code
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80",
              )}
              title={f.description}
            >
              {f.name}
              <span className="ml-1 opacity-70">({f.record_count})</span>
            </button>
          ))}
        </div>
      </ContentSheet>

      <ControlPanel>
        <Input
          className="max-w-md"
          placeholder={searchPlaceholder}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      {showProductionOrders ? (
        <ContentSheet className="overflow-hidden p-0">
          <div className="border-b border-border px-3 py-2">
            <h3 className="text-sm font-semibold">Production orders</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
                <tr>
                  {poColumns.map((col) => (
                    <th
                      key={col.key}
                      className={cn(
                        "px-3 py-2 font-medium",
                        col.className?.includes("text-right") ? "text-right" : "",
                      )}
                    >
                      {col.header}
                    </th>
                  ))}
                  {canWrite ? (
                    <th className="px-3 py-2 font-medium text-right">Actions</th>
                  ) : null}
                </tr>
              </thead>
              <tbody>
                {productionOrdersQuery.isLoading ? (
                  <tr>
                    <td colSpan={poColSpan} className="px-3 py-8 text-center text-muted-foreground">
                      Loading production orders…
                    </td>
                  </tr>
                ) : filteredPo.length === 0 ? (
                  <tr>
                    <td colSpan={poColSpan} className="px-3 py-8 text-center text-muted-foreground">
                      No production orders yet.
                    </td>
                  </tr>
                ) : (
                  filteredPo.map((po) => (
                    <tr key={po.id} className="border-b border-border/60">
                      {poColumns.map((col) => (
                        <td key={col.key} className={cn("px-3 py-2", col.className)}>
                          {col.cell(po)}
                        </td>
                      ))}
                      {canWrite ? (
                        <td className="px-3 py-2 text-right">
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setEditingPoId(po.id)
                              setPoDialogOpen(true)
                            }}
                          >
                            Edit
                          </Button>
                        </td>
                      ) : null}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </ContentSheet>
      ) : null}

      {activeFeature !== "production_orders" ? (
      <ContentSheet className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className={cn(
                      "px-3 py-2 font-medium",
                      col.className?.includes("text-right") ? "text-right" : "",
                    )}
                  >
                    {col.header}
                  </th>
                ))}
                {canWrite ? (
                  <th className="px-3 py-2 font-medium text-right">Actions</th>
                ) : null}
              </tr>
            </thead>
            <tbody>
              {recordsQuery.isLoading ? (
                <tr>
                  <td colSpan={colSpan} className="px-3 py-8 text-center text-muted-foreground">
                    Loading records…
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={colSpan} className="px-3 py-8 text-center text-muted-foreground">
                    No records for this filter.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <tr key={r.id} className="border-b border-border/60">
                    {columns.map((col) => (
                      <td key={col.key} className={cn("px-3 py-2", col.className)}>
                        {col.cell(r)}
                      </td>
                    ))}
                    {canWrite ? (
                      <td className="px-3 py-2 text-right">
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditingId(r.id)
                            setDialogOpen(true)
                          }}
                        >
                          Edit
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="text-destructive"
                          disabled={deleteMutation.isPending}
                          onClick={() => {
                            if (window.confirm(`Delete record ${r.reference}?`)) {
                              deleteMutation.mutate(r.id)
                            }
                          }}
                        >
                          Delete
                        </Button>
                      </td>
                    ) : null}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </ContentSheet>
      ) : null}

      <ProductionOrderFormDialog
        open={poDialogOpen}
        editingId={editingPoId}
        onClose={() => {
          setPoDialogOpen(false)
          setEditingPoId(null)
        }}
      />

      <ManufacturingRecordFormDialog
        open={dialogOpen}
        editingId={editingId}
        defaultFeatureCode={defaultFeatureCode}
        onClose={() => {
          setDialogOpen(false)
          setEditingId(null)
        }}
      />
    </div>
  )
}
