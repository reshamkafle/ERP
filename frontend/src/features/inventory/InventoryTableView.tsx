import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { InventoryItem, ItemLifecycleStatus } from "@/types/inventory"

function statusBadgeVariant(status: ItemLifecycleStatus) {
  if (status === "ACTIVE") return "success" as const
  if (status === "INACTIVE") return "secondary" as const
  if (status === "DISCONTINUED") return "warning" as const
  return "danger" as const
}

type InventoryTableViewProps = {
  items: InventoryItem[]
  lowStockIds: Set<number>
  isAdmin: boolean
  deletePending: boolean
  onEdit: (item: InventoryItem) => void
  onDelete: (item: InventoryItem) => void
}

export function InventoryTableView({
  items,
  lowStockIds,
  isAdmin,
  deletePending,
  onEdit,
  onDelete,
}: InventoryTableViewProps) {
  return (
    <div className="overflow-x-auto rounded-md border border-border">
      <table className="w-full min-w-[720px] text-left text-sm">
        <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
          <tr>
            <th className="px-3 py-2 font-medium">SKU</th>
            <th className="px-3 py-2 font-medium">Name</th>
            <th className="px-3 py-2 font-medium">Style</th>
            <th className="px-3 py-2 font-medium">Color</th>
            <th className="px-3 py-2 font-medium">Size</th>
            <th className="px-3 py-2 font-medium">Category</th>
            <th className="px-3 py-2 font-medium">Type</th>
            <th className="px-3 py-2 font-medium">ABC</th>
            <th className="px-3 py-2 font-medium">Reorder</th>
            <th className="px-3 py-2 font-medium">UOM</th>
            <th className="px-3 py-2 font-medium">Stock</th>
            <th className="px-3 py-2 font-medium">BOMs</th>
            <th className="px-3 py-2 font-medium">Status</th>
            <th className="px-3 py-2 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 ? null : (
            items.map((item) => (
              <tr key={item.id} className="border-b border-border last:border-0">
                <td className="px-3 py-2 font-mono text-xs">{item.sku}</td>
                <td className="px-3 py-2">
                  <div className="font-medium">{item.name}</div>
                  {item.barcode ? (
                    <p className="text-xs text-muted-foreground">{item.barcode}</p>
                  ) : null}
                </td>
                <td className="px-3 py-2 font-mono text-xs text-muted-foreground">
                  {item.style_code ?? item.template?.style_code ?? "—"}
                </td>
                <td className="px-3 py-2">{item.color ?? "—"}</td>
                <td className="px-3 py-2">{item.size ?? "—"}</td>
                <td className="px-3 py-2 text-muted-foreground">
                  {item.category?.name ?? "—"}
                </td>
                <td className="px-3 py-2">{item.item_type}</td>
                <td className="px-3 py-2">{item.abc_class ?? "—"}</td>
                <td className="px-3 py-2">{item.reorder_level}</td>
                <td className="px-3 py-2">{item.primary_uom}</td>
                <td className="px-3 py-2">
                  <span
                    className={
                      lowStockIds.has(item.id) ? "font-semibold text-destructive" : ""
                    }
                  >
                    {item.stock}
                  </span>
                  {lowStockIds.has(item.id) ? (
                    <Badge variant="danger" className="ml-2">
                      Low
                    </Badge>
                  ) : null}
                </td>
                <td className="px-3 py-2">
                  {item.manufacturing_item_sku ? (
                    <div className="space-y-1">
                      <span className="font-mono text-xs text-muted-foreground">
                        {item.manufacturing_item_sku}
                      </span>
                      {item.bom_parent_count > 0 ? (
                        <div className="flex flex-wrap items-center gap-1">
                          <span className="text-xs">
                            {item.bom_parent_count} BOM{item.bom_parent_count === 1 ? "" : "s"}
                          </span>
                          {item.has_bom_shortage ? (
                            <Badge variant="danger">BOM short</Badge>
                          ) : null}
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground">No parent BOMs</span>
                      )}
                    </div>
                  ) : (
                    <span className="text-xs text-muted-foreground">—</span>
                  )}
                </td>
                <td className="px-3 py-2">
                  <Badge variant={statusBadgeVariant(item.lifecycle_status)}>
                    {item.lifecycle_status}
                  </Badge>
                </td>
                <td className="px-3 py-2 text-right">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit(item)}
                  >
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
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
