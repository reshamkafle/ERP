import { useMemo } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { InventorySalesChart } from "@/features/inventory/InventorySalesChart"
import { formatMoney } from "@/lib/format-money"
import type { InventoryItem, ItemLifecycleStatus } from "@/types/inventory"

function statusBadgeVariant(status: ItemLifecycleStatus) {
  if (status === "ACTIVE") return "success" as const
  if (status === "INACTIVE") return "secondary" as const
  if (status === "DISCONTINUED") return "warning" as const
  return "danger" as const
}

function performanceLabel(quantitySold: number, maxSold: number): string {
  if (quantitySold <= 0 || maxSold <= 0) return "No sales"
  const ratio = quantitySold / maxSold
  if (ratio >= 0.66) return "High"
  if (ratio >= 0.33) return "Medium"
  return "Low"
}

function performanceVariant(label: string) {
  if (label === "High") return "success" as const
  if (label === "Medium") return "warning" as const
  if (label === "Low") return "secondary" as const
  return "secondary" as const
}

type InventoryGridViewProps = {
  items: InventoryItem[]
  lowStockIds: Set<number>
  isAdmin: boolean
  deletePending: boolean
  onEdit: (item: InventoryItem) => void
  onDelete: (item: InventoryItem) => void
}

function BomSection({ item }: { item: InventoryItem }) {
  if (!item.manufacturing_item_sku) {
    return <span className="text-xs text-muted-foreground">—</span>
  }
  return (
    <div className="space-y-1">
      <span className="font-mono text-xs text-muted-foreground">{item.manufacturing_item_sku}</span>
      {item.bom_parent_count > 0 ? (
        <div className="flex flex-wrap items-center gap-1">
          <span className="text-xs">
            {item.bom_parent_count} BOM{item.bom_parent_count === 1 ? "" : "s"}
          </span>
          {item.has_bom_shortage ? <Badge variant="danger">BOM short</Badge> : null}
        </div>
      ) : (
        <span className="text-xs text-muted-foreground">No parent BOMs</span>
      )}
    </div>
  )
}

function SalesSection({
  item,
  maxSold,
}: {
  item: InventoryItem
  maxSold: number
}) {
  const insight = item.sales_insight
  const lookback = insight?.lookback_days ?? 30
  const qty = insight?.quantity_sold ?? 0
  const revenue = insight?.revenue ?? "0"
  const dailyChart = insight?.daily_chart ?? []
  const perf = performanceLabel(qty, maxSold)

  return (
    <div className="space-y-3 rounded-lg border border-border bg-muted/30 p-3">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Sales performance
        </p>
        <p className="mt-1 text-xs text-muted-foreground">Last {lookback} days · units per day</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge variant={performanceVariant(perf)}>{perf}</Badge>
          <span className="text-sm tabular-nums">
            {qty} sold · {formatMoney(revenue)}
          </span>
        </div>
      </div>
      <InventorySalesChart dailyChart={dailyChart} lookbackDays={lookback} />
      <div className="grid gap-2 sm:grid-cols-2">
        <div>
          <p className="text-xs text-muted-foreground">Top buyer</p>
          <p className="text-sm font-medium">{insight?.top_buyer_name ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Top seller</p>
          <p className="truncate text-sm font-medium" title={insight?.top_seller_name ?? undefined}>
            {insight?.top_seller_name ?? "—"}
          </p>
        </div>
      </div>
    </div>
  )
}

export function InventoryGridView({
  items,
  lowStockIds,
  isAdmin,
  deletePending,
  onEdit,
  onDelete,
}: InventoryGridViewProps) {
  const maxSold = useMemo(
    () => Math.max(0, ...items.map((i) => i.sales_insight?.quantity_sold ?? 0)),
    [items],
  )

  if (items.length === 0) {
    return null
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {items.map((item) => (
        <Card key={item.id} className="flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="font-mono text-xs text-muted-foreground">{item.sku}</p>
                <CardTitle className="truncate text-base">{item.name}</CardTitle>
                {item.barcode ? (
                  <p className="truncate text-xs text-muted-foreground">{item.barcode}</p>
                ) : null}
              </div>
              <Badge variant={statusBadgeVariant(item.lifecycle_status)}>
                {item.lifecycle_status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col gap-3 pt-0">
            <dl className="grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
              <div>
                <dt className="text-xs text-muted-foreground">Category</dt>
                <dd>{item.category?.name ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground">Type</dt>
                <dd>{item.item_type}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground">UOM</dt>
                <dd>{item.primary_uom}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground">Stock</dt>
                <dd className="flex flex-wrap items-center gap-1">
                  <span
                    className={
                      lowStockIds.has(item.id) ? "font-semibold text-destructive tabular-nums" : "tabular-nums"
                    }
                  >
                    {item.stock}
                  </span>
                  {lowStockIds.has(item.id) ? (
                    <Badge variant="danger" className="text-[10px]">
                      Low
                    </Badge>
                  ) : null}
                </dd>
              </div>
            </dl>

            <div>
              <p className="mb-1 text-xs text-muted-foreground">BOMs</p>
              <BomSection item={item} />
            </div>

            <SalesSection item={item} maxSold={maxSold} />

            <div className="mt-auto flex flex-wrap gap-2 border-t border-border pt-3">
              <Button type="button" variant="outline" size="sm" onClick={() => onEdit(item)}>
                Edit
              </Button>
              {isAdmin ? (
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  disabled={deletePending}
                  onClick={() => onDelete(item)}
                >
                  Delete
                </Button>
              ) : null}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
