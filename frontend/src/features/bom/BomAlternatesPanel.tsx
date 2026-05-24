import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { addBomAlternate, addBomSubstitute } from "@/features/bom/bom-api"
import type { BOMLineRead, BOMRead, ManufacturingItem } from "@/types/bom"

type BomAlternatesPanelProps = {
  parentSku: string
  bom: BOMRead
  items: ManufacturingItem[]
}

export function BomAlternatesPanel({ parentSku, bom, items }: BomAlternatesPanelProps) {
  const queryClient = useQueryClient()
  const [altSku, setAltSku] = useState("")
  const [altGroup, setAltGroup] = useState("DEFAULT")
  const [altPriority, setAltPriority] = useState("1")
  const [altNotes, setAltNotes] = useState("")
  const [subLineId, setSubLineId] = useState<number | "">("")
  const [subSku, setSubSku] = useState("")
  const [subQty, setSubQty] = useState("1")
  const [subPriority, setSubPriority] = useState("1")
  const [subNotes, setSubNotes] = useState("")

  const alternateOptions = items.filter(
    (i) =>
      i.sku !== parentSku &&
      (i.category === "FINISHED_GOOD" || i.category === "SUB_ASSEMBLY"),
  )
  const substituteOptions = items.filter((i) => i.sku !== parentSku)
  const savedLines = bom.lines.filter((ln): ln is BOMLineRead & { line_id: number } =>
    ln.line_id != null,
  )

  const alternateMutation = useMutation({
    mutationFn: () =>
      addBomAlternate(parentSku, {
        alternate_parent_sku: altSku,
        alternate_group: altGroup.trim() || "DEFAULT",
        priority: parseInt(altPriority, 10) || 1,
        notes: altNotes.trim() || null,
      }),
    onSuccess: () => {
      toast.success("Alternate BOM added.")
      setAltSku("")
      setAltNotes("")
      void queryClient.invalidateQueries({ queryKey: ["bom"] })
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to add alternate BOM."
      toast.error(typeof detail === "string" ? detail : "Failed to add alternate BOM.")
    },
  })

  const substituteMutation = useMutation({
    mutationFn: () => {
      if (subLineId === "") throw new Error("Select a BOM line.")
      return addBomSubstitute(parentSku, subLineId, {
        substitute_sku: subSku,
        substitute_quantity: subQty,
        priority: parseInt(subPriority, 10) || 1,
        notes: subNotes.trim() || null,
      })
    },
    onSuccess: () => {
      toast.success("Substitute component added.")
      setSubSku("")
      setSubQty("1")
      setSubNotes("")
      void queryClient.invalidateQueries({ queryKey: ["bom"] })
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        (err as Error)?.message ??
        "Failed to add substitute."
      toast.error(typeof detail === "string" ? detail : "Failed to add substitute.")
    },
  })

  return (
    <div className="space-y-6">
      <section className="space-y-3 rounded-xl border border-border p-4">
        <h3 className="text-sm font-semibold text-foreground">Alternate BOMs</h3>
        <p className="text-sm text-muted-foreground">
          Link alternate style or sub-assembly BOMs for the same parent (priority within group).
        </p>
        {bom.alternates.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="border-b border-border text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-2 py-2 font-medium">Alternate SKU</th>
                  <th className="px-2 py-2 font-medium">Name</th>
                  <th className="px-2 py-2 font-medium">Group</th>
                  <th className="px-2 py-2 font-medium">Priority</th>
                  <th className="px-2 py-2 font-medium">Notes</th>
                </tr>
              </thead>
              <tbody>
                {bom.alternates.map((alt) => (
                  <tr key={alt.id} className="border-b border-border last:border-0">
                    <td className="px-2 py-2 font-mono text-xs">{alt.alternate_parent_sku}</td>
                    <td className="px-2 py-2">{alt.alternate_parent_name}</td>
                    <td className="px-2 py-2">{alt.alternate_group}</td>
                    <td className="px-2 py-2 tabular-nums">{alt.priority}</td>
                    <td className="px-2 py-2 text-muted-foreground">{alt.notes ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No alternate BOMs yet.</p>
        )}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <Select value={altSku} onChange={(e) => setAltSku(e.target.value)}>
            <option value="">Alternate style…</option>
            {alternateOptions.map((item) => (
              <option key={item.sku} value={item.sku}>
                {item.sku} — {item.name}
              </option>
            ))}
          </Select>
          <Input
            placeholder="Group"
            value={altGroup}
            onChange={(e) => setAltGroup(e.target.value)}
          />
          <Input
            type="number"
            min={1}
            placeholder="Priority"
            value={altPriority}
            onChange={(e) => setAltPriority(e.target.value)}
          />
          <Input
            placeholder="Notes"
            value={altNotes}
            onChange={(e) => setAltNotes(e.target.value)}
          />
          <Button
            type="button"
            size="sm"
            disabled={!altSku || alternateMutation.isPending}
            onClick={() => alternateMutation.mutate()}
          >
            Add alternate
          </Button>
        </div>
      </section>

      <section className="space-y-3 rounded-xl border border-border p-4">
        <h3 className="text-sm font-semibold text-foreground">Line substitutes</h3>
        <p className="text-sm text-muted-foreground">
          Approved replacement components for a BOM line (save the BOM first so lines have IDs).
        </p>
        {savedLines.some((ln) => ln.substitutes.length > 0) ? (
          <div className="space-y-4">
            {savedLines
              .filter((ln) => ln.substitutes.length > 0)
              .map((ln) => (
                <div key={ln.line_id} className="rounded-lg border border-border bg-muted/20 p-3">
                  <p className="text-sm font-medium">
                    Line {ln.line_sequence}: {ln.component_sku} — {ln.component_name}
                  </p>
                  <ul className="mt-2 space-y-1 text-sm">
                    {ln.substitutes.map((sub) => (
                      <li key={sub.id} className="flex flex-wrap gap-2 text-muted-foreground">
                        <span className="font-mono text-xs text-foreground">{sub.substitute_sku}</span>
                        <span>{sub.substitute_name}</span>
                        <span>× {sub.substitute_quantity}</span>
                        <span>priority {sub.priority}</span>
                        {sub.notes ? <span>({sub.notes})</span> : null}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No substitutes yet.</p>
        )}
        {savedLines.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Save the BOM to assign line IDs before adding substitutes.
          </p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
            <Select
              value={subLineId === "" ? "" : String(subLineId)}
              onChange={(e) =>
                setSubLineId(e.target.value ? parseInt(e.target.value, 10) : "")
              }
            >
              <option value="">BOM line…</option>
              {savedLines.map((ln) => (
                <option key={ln.line_id} value={ln.line_id}>
                  #{ln.line_sequence} {ln.component_sku}
                </option>
              ))}
            </Select>
            <Select value={subSku} onChange={(e) => setSubSku(e.target.value)}>
              <option value="">Substitute…</option>
              {substituteOptions.map((item) => (
                <option key={item.sku} value={item.sku}>
                  {item.sku} — {item.name}
                </option>
              ))}
            </Select>
            <Input
              type="number"
              min={0}
              step="any"
              placeholder="Qty"
              value={subQty}
              onChange={(e) => setSubQty(e.target.value)}
            />
            <Input
              type="number"
              min={1}
              placeholder="Priority"
              value={subPriority}
              onChange={(e) => setSubPriority(e.target.value)}
            />
            <Input
              placeholder="Notes"
              value={subNotes}
              onChange={(e) => setSubNotes(e.target.value)}
            />
            <Button
              type="button"
              size="sm"
              disabled={subLineId === "" || !subSku || substituteMutation.isPending}
              onClick={() => substituteMutation.mutate()}
            >
              Add substitute
            </Button>
          </div>
        )}
      </section>
    </div>
  )
}
