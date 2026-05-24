import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  createProductionOrder,
  fetchProductionOrder,
  updateProductionOrder,
  type ProductionOrderCreate,
} from "@/features/manufacturing/production-order-api"
import { api } from "@/lib/api"

type ProductOption = { id: number; name: string; sku: string }

type Props = {
  open: boolean
  editingId: number | null
  onClose: () => void
}

const PRIORITIES = ["HIGH", "MEDIUM", "LOW"] as const

export function ProductionOrderFormDialog({ open, editingId, onClose }: Props) {
  const queryClient = useQueryClient()
  const [productId, setProductId] = useState<number | "">("")
  const [quantityPlanned, setQuantityPlanned] = useState("1")
  const [priority, setPriority] = useState<string>("MEDIUM")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [routingId, setRoutingId] = useState<number | "">("")
  const [warehouseId, setWarehouseId] = useState<number | "">("")
  const [notes, setNotes] = useState("")

  const productsQuery = useQuery({
    queryKey: ["inventory-products-picker"],
    queryFn: async () => {
      const { data } = await api.get<{ items: ProductOption[] }>("/v1/inventory", {
        params: { limit: 200 },
      })
      return data.items ?? []
    },
    enabled: open,
  })

  const routingsQuery = useQuery({
    queryKey: ["manufacturing-routings"],
    queryFn: async () => {
      const { data } = await api.get<{ id: number; code: string; name: string }[]>(
        "/v1/manufacturing/routings",
      )
      return data
    },
    enabled: open,
  })

  const detailQuery = useQuery({
    queryKey: ["production-order", editingId],
    queryFn: () => fetchProductionOrder(editingId!),
    enabled: open && editingId != null,
  })

  useEffect(() => {
    if (!open) return
    if (editingId && detailQuery.data) {
      const po = detailQuery.data
      setProductId(po.product_id)
      setQuantityPlanned(String(po.quantity_planned))
      setPriority(po.priority)
      setStartDate(po.start_date ?? "")
      setEndDate(po.end_date ?? "")
      setRoutingId(po.routing_id ?? "")
      setWarehouseId(po.warehouse_id ?? "")
      setNotes(po.notes ?? "")
    } else if (!editingId) {
      setProductId("")
      setQuantityPlanned("1")
      setPriority("MEDIUM")
      setStartDate("")
      setEndDate("")
      setRoutingId("")
      setWarehouseId("")
      setNotes("")
    }
  }, [open, editingId, detailQuery.data])

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (productId === "") throw new Error("Product required")
      const body: ProductionOrderCreate = {
        product_id: Number(productId),
        quantity_planned: quantityPlanned,
        priority,
        start_date: startDate || null,
        end_date: endDate || null,
        routing_id: routingId === "" ? null : Number(routingId),
        warehouse_id: warehouseId === "" ? null : Number(warehouseId),
        notes: notes || null,
      }
      if (editingId) {
        return updateProductionOrder(editingId, body)
      }
      return createProductionOrder(body)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["production-orders"] })
      toast.success(editingId ? "Production order updated" : "Production order created")
      onClose()
    },
    onError: () => toast.error("Could not save production order"),
  })

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4">
      <div className="my-8 w-full max-w-lg rounded-lg border border-border bg-background p-6 shadow-lg">
        <h2 className="text-lg font-semibold">
          {editingId ? "Edit production order" : "New production order"}
        </h2>
        <p className="mt-1 text-xs text-muted-foreground">
          Operational work order — quantity, schedule, routing, and warehouses.
        </p>

        <div className="mt-4 grid gap-4">
          <div>
            <Label htmlFor="po-product">Product</Label>
            <select
              id="po-product"
              className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={productId}
              onChange={(e) => setProductId(e.target.value ? Number(e.target.value) : "")}
              disabled={!!editingId}
            >
              <option value="">— Select product —</option>
              {(productsQuery.data ?? []).map((p) => (
                <option key={p.id} value={p.id}>
                  {p.sku} — {p.name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="po-qty">Quantity planned</Label>
              <Input
                id="po-qty"
                type="number"
                min={0.0001}
                step="any"
                value={quantityPlanned}
                onChange={(e) => setQuantityPlanned(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="po-priority">Priority</Label>
              <select
                id="po-priority"
                className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="po-start">Start date</Label>
              <Input
                id="po-start"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="po-end">End date</Label>
              <Input
                id="po-end"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
          <div>
            <Label htmlFor="po-routing">Routing</Label>
            <select
              id="po-routing"
              className="mt-1 flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={routingId}
              onChange={(e) => setRoutingId(e.target.value ? Number(e.target.value) : "")}
            >
              <option value="">— None —</option>
              {(routingsQuery.data ?? []).map((r) => (
                <option key={r.id} value={r.id}>
                  {r.code} — {r.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label htmlFor="po-notes">Notes</Label>
            <textarea
              id="po-notes"
              className="mt-1 min-h-[72px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="button"
            data-testid="production-order-save"
            disabled={saveMutation.isPending || productId === ""}
            onClick={() => saveMutation.mutate()}
          >
            {saveMutation.isPending ? "Saving…" : "Save"}
          </Button>
        </div>
      </div>
    </div>
  )
}
