import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useMemo, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { Select } from "@/components/ui/select"
import {
  fetchMaterialRoll,
  fetchMaterialRolls,
  fetchRollLabelHtml,
  receiveMaterialRoll,
  scanMaterialRoll,
} from "@/features/material-rolls/material-rolls-api"
import { fetchInventory } from "@/features/inventory/inventory-api"
import type { MaterialRoll, MaterialRollDetail, MaterialRollStatus } from "@/types/material-roll"

const STATUSES: MaterialRollStatus[] = [
  "IN_STOCK",
  "ALLOCATED",
  "IN_PRODUCTION",
  "ON_HOLD",
  "QUARANTINED",
  "REJECTED",
  "SHIPPED",
]

export function FabricRollsPage() {
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const initialRollId = searchParams.get("roll")
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState<MaterialRollStatus | "">("")
  const [dyeLot, setDyeLot] = useState("")
  const [selectedId, setSelectedId] = useState<number | null>(
    initialRollId ? Number(initialRollId) : null,
  )
  const [scanInput, setScanInput] = useState("")
  const [receiveOpen, setReceiveOpen] = useState(false)
  const [receiveProductId, setReceiveProductId] = useState("")
  const [receiveQty, setReceiveQty] = useState("")

  const listQuery = useQuery({
    queryKey: ["material-rolls", search, status, dyeLot],
    queryFn: () =>
      fetchMaterialRolls({
        search: search || undefined,
        status: status || undefined,
        dye_lot: dyeLot || undefined,
        limit: 100,
      }),
  })

  const detailQuery = useQuery({
    queryKey: ["material-roll", selectedId],
    queryFn: () => fetchMaterialRoll(selectedId!),
    enabled: selectedId != null,
  })

  const productsQuery = useQuery({
    queryKey: ["inventory-raw-for-rolls"],
    queryFn: () => fetchInventory({ item_type: "RAW", limit: 200 }),
  })

  const scanMutation = useMutation({
    mutationFn: () => {
      const v = scanInput.trim()
      if (!v) throw new Error("Enter barcode or roll number")
      if (v.startsWith("ROLL-")) return scanMaterialRoll({ roll_number: v })
      return scanMaterialRoll({ barcode: v })
    },
    onSuccess: (data) => {
      setSelectedId(data.roll.id)
      toast.success(`Found roll ${data.roll.roll_number}`)
      void queryClient.invalidateQueries({ queryKey: ["material-rolls"] })
    },
    onError: (e: Error) => toast.error(e.message || "Roll not found"),
  })

  const receiveMutation = useMutation({
    mutationFn: () =>
      receiveMaterialRoll({
        product_id: Number(receiveProductId),
        initial_quantity: Number(receiveQty),
        primary_uom: "meter",
      }),
    onSuccess: (roll) => {
      toast.success(`Received roll ${roll.roll_number}`)
      setReceiveOpen(false)
      setReceiveQty("")
      void queryClient.invalidateQueries({ queryKey: ["material-rolls"] })
      setSelectedId(roll.id)
    },
    onError: () => toast.error("Failed to receive roll"),
  })

  const printLabel = async (rollId: number) => {
    try {
      const html = await fetchRollLabelHtml(rollId)
      const w = window.open("", "_blank", "width=320,height=480")
      if (!w) return
      // Security: use srcdoc instead of document.write to avoid executing inline scripts.
      const frame = w.document.createElement("iframe")
      frame.style.width = "100%"
      frame.style.height = "100%"
      frame.style.border = "none"
      frame.sandbox = "allow-modals allow-same-origin"
      frame.srcdoc = html
      w.document.body.replaceChildren(frame)
      w.document.title = "Roll label"
      frame.onload = () => w.print()
    } catch {
      toast.error("Could not load label")
    }
  }

  const rolls = listQuery.data?.items ?? []
  const detail: MaterialRollDetail | undefined = detailQuery.data

  const rawProducts = useMemo(
    () => productsQuery.data?.items.filter((p) => p.roll_tracking_enabled || p.item_type === "RAW") ?? [],
    [productsQuery.data],
  )

  return (
    <div className="space-y-4">
      <PageHeader
        title="Fabric rolls & lots"
        description="Roll-level traceability with barcode/RFID scan, receipt, and production issue."
        actions={
          <Button type="button" onClick={() => setReceiveOpen(true)}>
            Receive roll
          </Button>
        }
      />

      <ControlPanel>
        <div className="flex flex-wrap gap-2">
          <Input
            placeholder="Search roll, barcode, dye lot…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-xs"
          />
          <Select value={status} onChange={(e) => setStatus(e.target.value as MaterialRollStatus | "")}>
            <option value="">All statuses</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.replace(/_/g, " ")}
              </option>
            ))}
          </Select>
          <Input
            placeholder="Dye lot"
            value={dyeLot}
            onChange={(e) => setDyeLot(e.target.value)}
            className="max-w-[140px]"
          />
        </div>
        <div className="mt-3 flex flex-wrap gap-2 border-t border-border pt-3">
          <Input
            placeholder="Scan barcode or roll number"
            value={scanInput}
            onChange={(e) => setScanInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && scanMutation.mutate()}
            className="max-w-sm"
          />
          <Button
            type="button"
            variant="secondary"
            onClick={() => scanMutation.mutate()}
            disabled={scanMutation.isPending}
          >
            Scan lookup
          </Button>
        </div>
      </ControlPanel>

      <div className="grid gap-4 lg:grid-cols-2">
        <ContentSheet>
          {listQuery.isLoading ? (
            <LoadingSpinner />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="p-2">Roll #</th>
                    <th className="p-2">SKU</th>
                    <th className="p-2">Remaining</th>
                    <th className="p-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {rolls.map((r: MaterialRoll) => (
                    <tr
                      key={r.id}
                      className={`cursor-pointer border-b hover:bg-muted/50 ${selectedId === r.id ? "bg-muted" : ""}`}
                      onClick={() => setSelectedId(r.id)}
                    >
                      <td className="p-2 font-mono text-xs">{r.roll_number}</td>
                      <td className="p-2">{r.product_sku}</td>
                      <td className="p-2">
                        {r.remaining_quantity} {r.primary_uom}
                      </td>
                      <td className="p-2">{r.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {rolls.length === 0 && (
                <p className="p-4 text-sm text-muted-foreground">No rolls match your filters.</p>
              )}
            </div>
          )}
        </ContentSheet>

        <ContentSheet>
          {!selectedId ? (
            <p className="p-4 text-sm text-muted-foreground">Select a roll or scan a barcode.</p>
          ) : detailQuery.isLoading ? (
            <LoadingSpinner />
          ) : detail ? (
            <RollDetailPanel detail={detail} onPrint={() => void printLabel(detail.id)} />
          ) : null}
        </ContentSheet>
      </div>

      {receiveOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <ContentSheet className="w-full max-w-md space-y-3 p-4">
            <h2 className="text-lg font-semibold">Receive fabric roll</h2>
            <Select
              value={receiveProductId}
              onChange={(e) => setReceiveProductId(e.target.value)}
            >
              <option value="">Select raw material SKU</option>
              {rawProducts.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.sku} — {p.name}
                </option>
              ))}
            </Select>
            <Input
              type="number"
              placeholder="Length (meters)"
              value={receiveQty}
              onChange={(e) => setReceiveQty(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button type="button" variant="ghost" onClick={() => setReceiveOpen(false)}>
                Cancel
              </Button>
              <Button
                type="button"
                onClick={() => receiveMutation.mutate()}
                disabled={!receiveProductId || !receiveQty || receiveMutation.isPending}
              >
                Receive
              </Button>
            </div>
          </ContentSheet>
        </div>
      )}
    </div>
  )
}

function RollDetailPanel({
  detail,
  onPrint,
}: {
  detail: MaterialRollDetail
  onPrint: () => void
}) {
  return (
    <div className="space-y-4 p-2">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h2 className="font-mono text-lg font-semibold">{detail.roll_number}</h2>
          <p className="text-sm text-muted-foreground">
            {detail.product_sku} — {detail.product_name}
          </p>
        </div>
        <Button type="button" variant="outline" size="sm" onClick={onPrint}>
          Print label
        </Button>
      </div>
      <dl className="grid grid-cols-2 gap-2 text-sm">
        <dt className="text-muted-foreground">Remaining</dt>
        <dd>
          {detail.remaining_quantity} {detail.primary_uom}
        </dd>
        <dt className="text-muted-foreground">Color / dye lot</dt>
        <dd>
          {detail.color ?? "—"} / {detail.dye_lot ?? "—"}
        </dd>
        <dt className="text-muted-foreground">Barcode</dt>
        <dd className="font-mono text-xs">{detail.barcode ?? "—"}</dd>
        <dt className="text-muted-foreground">Status</dt>
        <dd>{detail.status}</dd>
        <dt className="text-muted-foreground">GRN</dt>
        <dd>{detail.grn_reference ?? "—"}</dd>
        {detail.last_scanned_at && (
          <>
            <dt className="text-muted-foreground">Last scanned</dt>
            <dd>{new Date(detail.last_scanned_at).toLocaleString()}</dd>
          </>
        )}
      </dl>
      <section>
        <h3 className="mb-2 text-sm font-semibold">Movements</h3>
        <ul className="max-h-40 space-y-1 overflow-y-auto text-xs">
          {detail.movements.map((m) => (
            <li key={m.id} className="rounded border px-2 py-1">
              {m.movement_type}: {m.quantity_delta} {m.uom}{" "}
              <span className="text-muted-foreground">
                {new Date(m.transaction_at).toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      </section>
      {detail.inspections.length > 0 && (
        <section>
          <h3 className="mb-2 text-sm font-semibold">Inspections</h3>
          <ul className="text-xs">
            {detail.inspections.map((i) => (
              <li key={i.id}>
                {i.passed ? "Pass" : "Fail"} — {new Date(i.inspected_at).toLocaleDateString()}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
