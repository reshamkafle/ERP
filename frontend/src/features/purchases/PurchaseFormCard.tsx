import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Trash2 } from "lucide-react"
import { useMemo, useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { createPurchase, fetchPurchaseProducts } from "@/features/purchases/purchases-api"
import { fetchSuppliers } from "@/features/suppliers/suppliers-api"
import { useDebouncedValue } from "@/features/pos/useDebouncedValue"
import { formatMoney } from "@/lib/format-money"
import type { PurchaseLineDraft, PurchaseProduct } from "@/types/purchase"

export function PurchaseFormCard() {
  const queryClient = useQueryClient()
  const [supplierId, setSupplierId] = useState("")
  const [search, setSearch] = useState("")
  const [lines, setLines] = useState<PurchaseLineDraft[]>([])
  const debouncedSearch = useDebouncedValue(search, 300)

  const suppliersQuery = useQuery({
    queryKey: ["suppliers", "list", ""],
    queryFn: () => fetchSuppliers({ limit: 200 }),
  })

  const productsQuery = useQuery({
    queryKey: ["purchases", "products", debouncedSearch],
    queryFn: () =>
      fetchPurchaseProducts({
        search: debouncedSearch || undefined,
        limit: 20,
      }),
    enabled: debouncedSearch.length > 0,
  })

  const total = useMemo(
    () =>
      lines.reduce((sum, line) => {
        const qty = line.quantity
        const cost = Number.parseFloat(line.unit_cost)
        if (!Number.isFinite(cost)) return sum
        return sum + qty * cost
      }, 0),
    [lines],
  )

  const createMutation = useMutation({
    mutationFn: createPurchase,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["purchases"] })
      void queryClient.invalidateQueries({ queryKey: ["suppliers"] })
      void queryClient.invalidateQueries({ queryKey: ["inventory"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success("Purchase recorded — stock updated")
      setSupplierId("")
      setSearch("")
      setLines([])
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not create purchase"
      toast.error(typeof detail === "string" ? detail : "Could not create purchase")
    },
  })

  const suppliers = suppliersQuery.data?.items ?? []
  const products = productsQuery.data?.items ?? []

  function addProduct(product: PurchaseProduct) {
    setLines((prev) => {
      const existing = prev.find((l) => l.product_id === product.id)
      if (existing) {
        return prev.map((l) =>
          l.product_id === product.id ? { ...l, quantity: l.quantity + 1 } : l,
        )
      }
      return [
        ...prev,
        {
          product_id: product.id,
          sku: product.sku,
          name: product.name,
          quantity: 1,
          unit_cost: product.cost_price,
        },
      ]
    })
    setSearch("")
  }

  function updateLine(productId: number, patch: Partial<PurchaseLineDraft>) {
    setLines((prev) => prev.map((l) => (l.product_id === productId ? { ...l, ...patch } : l)))
  }

  function removeLine(productId: number) {
    setLines((prev) => prev.filter((l) => l.product_id !== productId))
  }

  function handleSubmit() {
    const sid = Number(supplierId)
    if (!sid) {
      toast.error("Select a supplier")
      return
    }
    if (lines.length === 0) {
      toast.error("Add at least one product")
      return
    }
    for (const line of lines) {
      const cost = Number.parseFloat(line.unit_cost)
      if (!Number.isFinite(cost) || cost < 0) {
        toast.error(`Invalid unit cost for ${line.sku}`)
        return
      }
      if (line.quantity < 1) {
        toast.error(`Invalid quantity for ${line.sku}`)
        return
      }
    }
    createMutation.mutate({
      supplier_id: sid,
      items: lines.map((l) => ({
        product_id: l.product_id,
        quantity: l.quantity,
        unit_cost: Number.parseFloat(l.unit_cost),
      })),
    })
  }

  return (
    <div className="space-y-4 rounded-xl border border-border bg-card p-4">
      <div>
        <h2 className="text-lg font-semibold text-foreground">New purchase</h2>
        <p className="text-sm text-muted-foreground">
          Receive stock from a supplier. Quantities increase inventory in one transaction.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Supplier">
          <Select
            value={supplierId}
            onChange={(e) => setSupplierId(e.target.value)}
          >
            <option value="">Select supplier…</option>
            {suppliers.map((s) => (
              <option key={s.id} value={String(s.id)}>
                {s.name}
              </option>
            ))}
          </Select>
          {suppliers.length === 0 && !suppliersQuery.isLoading ? (
            <p className="mt-1 text-xs text-muted-foreground">
              Add a supplier first from the Suppliers page.
            </p>
          ) : null}
        </Field>
        <Field label="Search products">
          <Input
            placeholder="SKU, name, or barcode…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </Field>
      </div>

      {debouncedSearch ? (
        <div className="max-h-48 overflow-y-auto rounded-lg border border-border">
          {productsQuery.isLoading ? (
            <p className="p-3 text-sm text-muted-foreground">Searching…</p>
          ) : products.length === 0 ? (
            <p className="p-3 text-sm text-muted-foreground">No products found.</p>
          ) : (
            <ul className="divide-y divide-border">
              {products.map((product) => (
                <li
                  key={product.id}
                  className="flex items-center justify-between gap-2 px-3 py-2 text-sm"
                >
                  <div>
                    <p className="font-medium">{product.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {product.sku} · stock {product.stock} · cost {formatMoney(product.cost_price)}
                    </p>
                  </div>
                  <Button type="button" size="sm" variant="outline" onClick={() => addProduct(product)}>
                    <Plus className="size-4" />
                    Add
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : null}

      {lines.length > 0 ? (
        <LinesTable
          lines={lines}
          total={total}
          onUpdate={updateLine}
          onRemove={removeLine}
        />
      ) : null}

      <div className="flex flex-col gap-3 border-t border-border pt-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-lg font-semibold tabular-nums">
          Total: <span className="text-emerald-600 dark:text-emerald-400">{formatMoney(total)}</span>
        </p>
        <Button
          type="button"
          disabled={createMutation.isPending || lines.length === 0}
          onClick={handleSubmit}
        >
          {createMutation.isPending ? "Saving…" : "Record purchase"}
        </Button>
      </div>
    </div>
  )
}

function LinesTable({
  lines,
  total,
  onUpdate,
  onRemove,
}: {
  lines: PurchaseLineDraft[]
  total: number
  onUpdate: (productId: number, patch: Partial<PurchaseLineDraft>) => void
  onRemove: (productId: number) => void
}) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full min-w-[560px] text-left text-sm">
        <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
          <tr>
            <th className="px-3 py-2 font-medium">Product</th>
            <th className="px-3 py-2 font-medium">Qty</th>
            <th className="px-3 py-2 font-medium">Unit cost</th>
            <th className="px-3 py-2 font-medium text-right">Line total</th>
            <th className="px-3 py-2 w-10" />
          </tr>
        </thead>
        <tbody>
          {lines.map((line) => {
            const cost = Number.parseFloat(line.unit_cost)
            const lineTotal = Number.isFinite(cost) ? line.quantity * cost : 0
            return (
              <tr key={line.product_id} className="border-b border-border last:border-0">
                <td className="px-3 py-2">
                  <p className="font-medium">{line.name}</p>
                  <p className="text-xs text-muted-foreground">{line.sku}</p>
                </td>
                <td className="px-3 py-2">
                  <Input
                    type="number"
                    min={1}
                    className="w-20"
                    value={line.quantity}
                    onChange={(e) =>
                      onUpdate(line.product_id, {
                        quantity: Math.max(1, Number.parseInt(e.target.value, 10) || 1),
                      })
                    }
                  />
                </td>
                <td className="px-3 py-2">
                  <Input
                    type="number"
                    min={0}
                    step="0.01"
                    className="w-28"
                    value={line.unit_cost}
                    onChange={(e) => onUpdate(line.product_id, { unit_cost: e.target.value })}
                  />
                </td>
                <td className="px-3 py-2 text-right tabular-nums font-medium">
                  {formatMoney(lineTotal)}
                </td>
                <td className="px-3 py-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    aria-label="Remove line"
                    onClick={() => onRemove(line.product_id)}
                  >
                    <Trash2 className="size-4 text-destructive" />
                  </Button>
                </td>
              </tr>
            )
          })}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={3} className="px-3 py-2 text-right text-xs uppercase text-muted-foreground">
              Total
            </td>
            <td className="px-3 py-2 text-right font-semibold tabular-nums">
              {formatMoney(total)}
            </td>
            <td />
          </tr>
        </tfoot>
      </table>
    </div>
  )
}

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <div>
      <Label className="mb-1 block">{label}</Label>
      {children}
    </div>
  )
}
