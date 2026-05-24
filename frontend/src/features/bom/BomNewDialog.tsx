import { useMemo } from "react"

import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import type { BOMSummary, ManufacturingItem } from "@/types/bom"

type Props = {
  open: boolean
  parents: ManufacturingItem[]
  existingBoms: BOMSummary[]
  onClose: () => void
  onSelect: (sku: string) => void
}

export function BomNewDialog({
  open,
  parents,
  existingBoms,
  onClose,
  onSelect,
}: Props) {
  const parentsWithoutBom = useMemo(() => {
    const withBom = new Set(existingBoms.map((b) => b.parent_sku))
    return parents.filter((p) => !withBom.has(p.sku))
  }, [parents, existingBoms])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="new-bom-title"
    >
      <div className="w-full max-w-md rounded-xl border border-border bg-background p-6 shadow-lg">
        <h2 id="new-bom-title" className="text-lg font-semibold text-foreground">
          New BOM
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose a finished good or sub-assembly that does not have a BOM yet.
        </p>

        {parentsWithoutBom.length === 0 ? (
          <p className="mt-4 text-sm text-muted-foreground">
            Every style and assembly already has a BOM. Add a new manufacturing item
            first, or open an existing BOM to edit it.
          </p>
        ) : (
          <form
            className="mt-4 space-y-4"
            onSubmit={(e) => {
              e.preventDefault()
              const fd = new FormData(e.currentTarget)
              const sku = String(fd.get("parent_sku") ?? "")
              if (sku) onSelect(sku)
            }}
          >
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground" htmlFor="new-bom-parent">
                Parent item
              </label>
              <Select id="new-bom-parent" name="parent_sku" required defaultValue="">
                <option value="" disabled>
                  Select style / assembly…
                </option>
                {parentsWithoutBom.map((item) => (
                  <option key={item.sku} value={item.sku}>
                    {item.sku} — {item.name} ({item.category})
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit">Continue</Button>
            </div>
          </form>
        )}

        {parentsWithoutBom.length === 0 ? (
          <div className="mt-4 flex justify-end">
            <Button type="button" variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        ) : null}
      </div>
    </div>
  )
}
