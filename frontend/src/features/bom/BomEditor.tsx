import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo, useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { fetchBomItems, saveBom, updateBomStatus } from "@/features/bom/bom-api"
import { BomAlternatesPanel } from "@/features/bom/BomAlternatesPanel"
import type {
  BOMHeaderInput,
  BOMLineInput,
  BOMRead,
  BOMStatus,
  BOMType,
  ConsumptionType,
  ManufacturingItem,
} from "@/types/bom"

const STATUS_OPTIONS: { value: BOMStatus; label: string }[] = [
  { value: "DRAFT", label: "Draft" },
  { value: "ACTIVE", label: "Active" },
  { value: "OBSOLETE", label: "Obsolete" },
  { value: "SUPERSEDED", label: "Superseded" },
]

const BOM_TYPE_OPTIONS: { value: BOMType; label: string }[] = [
  { value: "MANUFACTURING", label: "Manufacturing" },
  { value: "ENGINEERING", label: "Engineering" },
  { value: "SALES", label: "Sales" },
  { value: "SERVICE", label: "Service" },
  { value: "PHANTOM", label: "Phantom" },
]

const CONSUMPTION_OPTIONS: { value: ConsumptionType; label: string }[] = [
  { value: "FABRIC", label: "Fabric" },
  { value: "TRIM", label: "Trim" },
  { value: "OTHER", label: "Other" },
]

function emptyLine(seq: number): BOMLineInput {
  return {
    component_sku: "",
    line_sequence: seq,
    quantity_per_unit: "1",
    consumption_type: "OTHER",
    wastage_percentage: "0",
    yield_percentage: "0",
    is_phantom: false,
    lead_time_offset_days: null,
    notes: null,
  }
}

function bomToDraft(bom: BOMRead): { header: BOMHeaderInput; lines: BOMLineInput[] } {
  return {
    header: {
      status: bom.status,
      bom_type: bom.bom_type,
      effective_start_date: bom.effective_start_date,
      effective_end_date: bom.effective_end_date,
      eco_number: bom.eco_number,
    },
    lines:
      bom.lines.length > 0
        ? bom.lines.map((ln) => ({
            component_sku: ln.component_sku,
            line_sequence: ln.line_sequence,
            quantity_per_unit: ln.quantity_per_unit,
            consumption_type: ln.consumption_type,
            wastage_percentage: ln.wastage_percentage,
            yield_percentage: ln.yield_percentage,
            is_phantom: ln.is_phantom,
            lead_time_offset_days: ln.lead_time_offset_days,
            notes: ln.notes,
          }))
        : [emptyLine(1)],
  }
}

type BomEditorProps = {
  parentSku: string
  bom: BOMRead
  isNew?: boolean
  onCancel: () => void
  onSaved: () => void
}

export function BomEditor({ parentSku, bom, isNew = false, onCancel, onSaved }: BomEditorProps) {
  const queryClient = useQueryClient()
  const [header, setHeader] = useState<BOMHeaderInput>(() => bomToDraft(bom).header)
  const [lines, setLines] = useState<BOMLineInput[]>(() => bomToDraft(bom).lines)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  useEffect(() => {
    const draft = bomToDraft(bom)
    setHeader(draft.header)
    setLines(draft.lines)
  }, [bom])

  const itemsQuery = useQuery({
    queryKey: ["bom", "items"],
    queryFn: () => fetchBomItems(),
  })

  const componentOptions = useMemo(
    () => (itemsQuery.data ?? []).filter((i) => i.sku !== parentSku),
    [itemsQuery.data, parentSku],
  )

  const saveMutation = useMutation({
    mutationFn: () => saveBom(parentSku, { header, lines }),
    onSuccess: (res) => {
      const msg = res.validation.is_valid
        ? isNew
          ? "BOM created."
          : "BOM saved."
        : `Saved with warnings: ${res.validation.warnings.join("; ")}`
      setSaveMessage(msg)
      toast.success(msg)
      void queryClient.invalidateQueries({ queryKey: ["bom"] })
      onSaved()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        (err as Error)?.message ??
        "Failed to save BOM."
      const message = typeof detail === "string" ? detail : "Failed to save BOM."
      setSaveMessage(message)
      toast.error(message)
    },
  })

  const activateMutation = useMutation({
    mutationFn: () => updateBomStatus(parentSku, "ACTIVE"),
    onSuccess: () => {
      setHeader((h) => ({ ...h, status: "ACTIVE" }))
      toast.success("BOM activated.")
      void queryClient.invalidateQueries({ queryKey: ["bom"] })
      onSaved()
    },
  })

  const updateLine = (index: number, patch: Partial<BOMLineInput>) => {
    setLines((prev) => prev.map((ln, i) => (i === index ? { ...ln, ...patch } : ln)))
  }

  const addLine = () => {
    setLines((prev) => [...prev, emptyLine(prev.length + 1)])
  }

  const removeLine = (index: number) => {
    setLines((prev) =>
      prev
        .filter((_, i) => i !== index)
        .map((ln, i) => ({ ...ln, line_sequence: i + 1 })),
    )
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-foreground">
          {isNew ? "Create BOM" : "Edit BOM"}
        </h2>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="outline" size="sm" onClick={onCancel}>
            Cancel
          </Button>
          {!isNew && header.status !== "ACTIVE" ? (
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled={activateMutation.isPending}
              onClick={() => activateMutation.mutate()}
            >
              Activate
            </Button>
          ) : null}
          <Button
            type="button"
            size="sm"
            disabled={saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            {saveMutation.isPending ? "Saving…" : isNew ? "Create BOM" : "Save BOM"}
          </Button>
        </div>
      </div>

      {saveMessage ? (
        <p className="text-sm text-muted-foreground">{saveMessage}</p>
      ) : null}

      <div className="grid gap-4 rounded-xl border border-border bg-muted/20 p-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="space-y-1 sm:col-span-2">
          <p className="text-xs font-medium text-muted-foreground">Parent</p>
          <p className="text-sm text-foreground">
            {bom.parent_sku} — {bom.parent_name}
          </p>
        </div>
        {!isNew ? (
          <>
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">BOM number</p>
              <p className="font-mono text-sm text-foreground">{bom.bom_number}</p>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">Version</p>
              <p className="text-sm text-foreground">v{bom.version}</p>
            </div>
          </>
        ) : (
          <div className="space-y-1 sm:col-span-2">
            <p className="text-xs font-medium text-muted-foreground">First save</p>
            <p className="text-sm text-muted-foreground">
              BOM number and version are assigned when you save.
            </p>
          </div>
        )}
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="bom-status">
            Status
          </label>
          <Select
            id="bom-status"
            value={header.status}
            onChange={(e) =>
              setHeader((h) => ({ ...h, status: e.target.value as BOMStatus }))
            }
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </Select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="bom-type">
            BOM type
          </label>
          <Select
            id="bom-type"
            value={header.bom_type}
            onChange={(e) =>
              setHeader((h) => ({ ...h, bom_type: e.target.value as BOMType }))
            }
          >
            {BOM_TYPE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </Select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="eco-number">
            ECO number
          </label>
          <Input
            id="eco-number"
            value={header.eco_number ?? ""}
            onChange={(e) =>
              setHeader((h) => ({ ...h, eco_number: e.target.value || null }))
            }
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="eff-start">
            Effective start
          </label>
          <Input
            id="eff-start"
            type="date"
            value={header.effective_start_date ?? ""}
            onChange={(e) =>
              setHeader((h) => ({
                ...h,
                effective_start_date: e.target.value || null,
              }))
            }
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="eff-end">
            Effective end
          </label>
          <Input
            id="eff-end"
            type="date"
            value={header.effective_end_date ?? ""}
            onChange={(e) =>
              setHeader((h) => ({
                ...h,
                effective_end_date: e.target.value || null,
              }))
            }
          />
        </div>
      </div>

      {bom.parent_product_snapshot ? (
        <div className="rounded-lg border border-border px-4 py-3 text-sm">
          <span className="font-medium">Linked product:</span>{" "}
          {bom.parent_product_snapshot.sku} — {bom.parent_product_snapshot.name}
          {bom.parent_product_snapshot.hs_code ? (
            <span className="ml-2 text-muted-foreground">
              HS {bom.parent_product_snapshot.hs_code}
            </span>
          ) : null}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          Link this style to an inventory product for full item master fields on components.
        </p>
      )}

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[1100px] text-left text-sm">
          <thead className="border-b border-border bg-muted/50 text-muted-foreground">
            <tr>
              <th className="px-2 py-2 font-medium">#</th>
              <th className="px-2 py-2 font-medium">Component</th>
              <th className="px-2 py-2 font-medium">Qty</th>
              <th className="px-2 py-2 font-medium">Consumption</th>
              <th className="px-2 py-2 font-medium">Wastage %</th>
              <th className="px-2 py-2 font-medium">Yield %</th>
              <th className="px-2 py-2 font-medium">Phantom</th>
              <th className="px-2 py-2 font-medium">LT offset</th>
              <th className="px-2 py-2 font-medium">Supplier</th>
              <th className="px-2 py-2 font-medium">HS code</th>
              <th className="px-2 py-2 font-medium" />
            </tr>
          </thead>
          <tbody>
            {lines.map((line, index) => {
              const readLine = bom.lines.find((l) => l.line_sequence === line.line_sequence)
              const snap = readLine?.product_snapshot
              return (
                <tr key={index} className="border-b border-border align-top last:border-0">
                  <td className="px-2 py-2">
                    <Input
                      type="number"
                      min={1}
                      className="w-14"
                      value={line.line_sequence ?? index + 1}
                      onChange={(e) =>
                        updateLine(index, {
                          line_sequence: parseInt(e.target.value, 10) || index + 1,
                        })
                      }
                    />
                  </td>
                  <td className="px-2 py-2">
                    <Select
                      value={line.component_sku}
                      onChange={(e) =>
                        updateLine(index, { component_sku: e.target.value })
                      }
                    >
                      <option value="">Select…</option>
                      {componentOptions.map((item: ManufacturingItem) => (
                        <option key={item.sku} value={item.sku}>
                          {item.sku} — {item.name}
                        </option>
                      ))}
                    </Select>
                  </td>
                  <td className="px-2 py-2">
                    <Input
                      type="number"
                      min={0}
                      step="any"
                      className="w-20"
                      value={line.quantity_per_unit}
                      onChange={(e) =>
                        updateLine(index, { quantity_per_unit: e.target.value })
                      }
                    />
                  </td>
                  <td className="px-2 py-2">
                    <Select
                      value={line.consumption_type}
                      onChange={(e) =>
                        updateLine(index, {
                          consumption_type: e.target.value as ConsumptionType,
                        })
                      }
                    >
                      {CONSUMPTION_OPTIONS.map((o) => (
                        <option key={o.value} value={o.value}>
                          {o.label}
                        </option>
                      ))}
                    </Select>
                  </td>
                  <td className="px-2 py-2">
                    <Input
                      type="number"
                      min={0}
                      step="any"
                      className="w-16"
                      value={line.wastage_percentage}
                      onChange={(e) =>
                        updateLine(index, { wastage_percentage: e.target.value })
                      }
                    />
                  </td>
                  <td className="px-2 py-2">
                    <Input
                      type="number"
                      min={0}
                      max={100}
                      step="any"
                      className="w-16"
                      value={line.yield_percentage}
                      onChange={(e) =>
                        updateLine(index, { yield_percentage: e.target.value })
                      }
                    />
                  </td>
                  <td className="px-2 py-2 text-center">
                    <input
                      type="checkbox"
                      checked={line.is_phantom}
                      onChange={(e) =>
                        updateLine(index, { is_phantom: e.target.checked })
                      }
                    />
                  </td>
                  <td className="px-2 py-2">
                    <Input
                      type="number"
                      min={0}
                      className="w-16"
                      value={line.lead_time_offset_days ?? ""}
                      onChange={(e) =>
                        updateLine(index, {
                          lead_time_offset_days: e.target.value
                            ? parseInt(e.target.value, 10)
                            : null,
                        })
                      }
                    />
                  </td>
                  <td className="px-2 py-2 text-muted-foreground">
                    {snap?.default_supplier_name ?? "—"}
                  </td>
                  <td className="px-2 py-2 text-muted-foreground">{snap?.hs_code ?? "—"}</td>
                  <td className="px-2 py-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeLine(index)}
                    >
                      Remove
                    </Button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <Button type="button" variant="outline" size="sm" onClick={addLine}>
        Add line
      </Button>

      {!isNew ? (
        <BomAlternatesPanel
          parentSku={parentSku}
          bom={bom}
          items={itemsQuery.data ?? []}
        />
      ) : null}
    </section>
  )
}
