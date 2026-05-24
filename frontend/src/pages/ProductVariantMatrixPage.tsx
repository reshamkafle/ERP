import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { PageHeader } from "@/components/PageHeader"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { Select } from "@/components/ui/select"
import { fetchCategories } from "@/features/inventory/inventory-api"
import {
  createProductTemplate,
  fetchProductAttributes,
  fetchProductTemplates,
  fetchTemplateVariants,
  generateVariantMatrix,
} from "@/features/inventory/product-variant-api"
import type { ProductTemplate } from "@/types/product-variant"

const ITEM_TYPES = [
  "RAW",
  "FINISHED",
  "SEMI_FINISHED",
  "CONSUMABLE",
  "TRADING",
  "SERVICE",
  "ASSET",
] as const

export function ProductVariantMatrixPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [colorIds, setColorIds] = useState<number[]>([])
  const [sizeIds, setSizeIds] = useState<number[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({
    style_code: "",
    name: "",
    sku_prefix: "",
    category_id: "",
    item_type: "FINISHED",
    manufacturing_item_sku: "",
  })

  const templatesQuery = useQuery({
    queryKey: ["product-templates", search],
    queryFn: () => fetchProductTemplates({ search: search || undefined, limit: 100 }),
  })

  const attributesQuery = useQuery({
    queryKey: ["product-attributes"],
    queryFn: fetchProductAttributes,
  })

  const categoriesQuery = useQuery({
    queryKey: ["inventory", "categories"],
    queryFn: fetchCategories,
  })

  const variantsQuery = useQuery({
    queryKey: ["template-variants", selectedId],
    queryFn: () => fetchTemplateVariants(selectedId!),
    enabled: selectedId != null,
  })

  const colorValues = useMemo(
    () => attributesQuery.data?.find((a) => a.code === "COLOR")?.values ?? [],
    [attributesQuery.data],
  )
  const sizeValues = useMemo(
    () => attributesQuery.data?.find((a) => a.code === "SIZE")?.values ?? [],
    [attributesQuery.data],
  )

  const createMutation = useMutation({
    mutationFn: createProductTemplate,
    onSuccess: (t) => {
      toast.success(`Style ${t.style_code} created`)
      setShowCreate(false)
      setSelectedId(t.id)
      void queryClient.invalidateQueries({ queryKey: ["product-templates"] })
    },
    onError: () => toast.error("Could not create style template"),
  })

  const matrixMutation = useMutation({
    mutationFn: () =>
      generateVariantMatrix(selectedId!, {
        color_value_ids: colorIds,
        size_value_ids: sizeIds,
        skip_existing: true,
        initial_stock: 0,
      }),
    onSuccess: (result) => {
      toast.success(`Created ${result.created.length} variant(s)`)
      if (result.skipped.length) {
        toast.message(`Skipped ${result.skipped.length} existing SKU(s)`)
      }
      if (result.errors.length) {
        toast.error(result.errors.join("; "))
      }
      void queryClient.invalidateQueries({ queryKey: ["template-variants", selectedId] })
      void queryClient.invalidateQueries({ queryKey: ["product-templates"] })
      void queryClient.invalidateQueries({ queryKey: ["inventory"] })
    },
    onError: () => toast.error("Matrix generation failed"),
  })

  function toggleId(list: number[], id: number): number[] {
    return list.includes(id) ? list.filter((x) => x !== id) : [...list, id]
  }

  function selectAllColors() {
    setColorIds(colorValues.map((v) => v.id))
  }

  function selectAllSizes() {
    setSizeIds(sizeValues.map((v) => v.id))
  }

  const selectedTemplate: ProductTemplate | undefined = templatesQuery.data?.items.find(
    (t) => t.id === selectedId,
  )

  return (
    <div className="space-y-6">
      <PageHeader
        title="Style–Color–Size matrix"
        description="Manage style templates and generate variant SKUs from color × size combinations."
        actions={
          <Link to="/inventory">
            <Button type="button" variant="outline" size="sm">
              Back to inventory
            </Button>
          </Link>
        }
      />

      <ControlPanel>
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[200px] flex-1">
            <Label htmlFor="template-search">Search styles</Label>
            <Input
              id="template-search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Style code or name"
            />
          </div>
          <Button type="button" onClick={() => setShowCreate((v) => !v)}>
            {showCreate ? "Cancel" : "New style template"}
          </Button>
        </div>
      </ControlPanel>

      {showCreate ? (
        <div className="rounded-md border border-border p-4 space-y-3">
          <h2 className="text-sm font-semibold">New style template</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <Label>Style code</Label>
              <Input
                value={form.style_code}
                onChange={(e) => setForm((f) => ({ ...f, style_code: e.target.value }))}
                placeholder="CLASSIC-SHIRT"
              />
            </div>
            <div>
              <Label>Name</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div>
              <Label>SKU prefix</Label>
              <Input
                value={form.sku_prefix}
                onChange={(e) => setForm((f) => ({ ...f, sku_prefix: e.target.value }))}
                placeholder="SHIRT"
              />
            </div>
            <div>
              <Label>Category</Label>
              <Select
                value={form.category_id}
                onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}
              >
                <option value="">—</option>
                {(categoriesQuery.data ?? []).map((c) => (
                  <option key={c.id} value={String(c.id)}>
                    {c.name}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <Label>Item type</Label>
              <Select
                value={form.item_type}
                onChange={(e) => setForm((f) => ({ ...f, item_type: e.target.value }))}
              >
                {ITEM_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <Label>Mfg style SKU (optional)</Label>
              <Input
                value={form.manufacturing_item_sku}
                onChange={(e) =>
                  setForm((f) => ({ ...f, manufacturing_item_sku: e.target.value }))
                }
                placeholder="STYLE-001"
              />
            </div>
          </div>
          <Button
            type="button"
            disabled={createMutation.isPending || !form.style_code || !form.name || !form.sku_prefix}
            onClick={() =>
              createMutation.mutate({
                style_code: form.style_code.trim(),
                name: form.name.trim(),
                sku_prefix: form.sku_prefix.trim(),
                category_id: form.category_id ? Number(form.category_id) : null,
                item_type: form.item_type as (typeof ITEM_TYPES)[number],
                manufacturing_item_sku: form.manufacturing_item_sku.trim() || null,
              })
            }
          >
            Create template
          </Button>
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-md border border-border overflow-hidden">
          <div className="border-b border-border bg-muted/50 px-3 py-2 text-xs font-medium uppercase text-muted-foreground">
            Style templates
          </div>
          {templatesQuery.isLoading ? (
            <div className="p-6 flex justify-center">
              <LoadingSpinner />
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-muted-foreground">
                  <th className="px-3 py-2">Style</th>
                  <th className="px-3 py-2">Variants</th>
                  <th className="px-3 py-2">Stock</th>
                </tr>
              </thead>
              <tbody>
                {(templatesQuery.data?.items ?? []).map((t) => (
                  <tr
                    key={t.id}
                    className={`border-b border-border cursor-pointer hover:bg-muted/30 ${
                      selectedId === t.id ? "bg-muted/50" : ""
                    }`}
                    onClick={() => setSelectedId(t.id)}
                  >
                    <td className="px-3 py-2">
                      <div className="font-mono text-xs">{t.style_code}</div>
                      <div>{t.name}</div>
                    </td>
                    <td className="px-3 py-2">{t.variant_count}</td>
                    <td className="px-3 py-2">{t.total_stock}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="space-y-4">
          {selectedId == null ? (
            <p className="text-sm text-muted-foreground">Select a style template to build the matrix.</p>
          ) : (
            <>
              <div>
                <h2 className="font-semibold">{selectedTemplate?.name}</h2>
                <p className="text-sm text-muted-foreground font-mono">
                  Prefix: {selectedTemplate?.sku_prefix} · Pattern:{" "}
                  {`{prefix}-{color}-{size}`}
                </p>
              </div>

              <div className="rounded-md border border-border p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Colors</Label>
                  <Button type="button" variant="ghost" size="sm" onClick={selectAllColors}>
                    Select all
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {colorValues.map((v) => (
                    <label key={v.id} className="flex items-center gap-1 text-sm">
                      <input
                        type="checkbox"
                        checked={colorIds.includes(v.id)}
                        onChange={() => setColorIds((ids) => toggleId(ids, v.id))}
                      />
                      {v.label}
                    </label>
                  ))}
                </div>
              </div>

              <div className="rounded-md border border-border p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Sizes</Label>
                  <Button type="button" variant="ghost" size="sm" onClick={selectAllSizes}>
                    Select all
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {sizeValues.map((v) => (
                    <label key={v.id} className="flex items-center gap-1 text-sm">
                      <input
                        type="checkbox"
                        checked={sizeIds.includes(v.id)}
                        onChange={() => setSizeIds((ids) => toggleId(ids, v.id))}
                      />
                      {v.label}
                    </label>
                  ))}
                </div>
              </div>

              <Button
                type="button"
                disabled={
                  matrixMutation.isPending ||
                  colorIds.length === 0 ||
                  sizeIds.length === 0
                }
                onClick={() => matrixMutation.mutate()}
              >
                Generate {colorIds.length * sizeIds.length} variant SKU(s)
              </Button>

              <div className="rounded-md border border-border overflow-hidden">
                <div className="border-b border-border bg-muted/50 px-3 py-2 text-xs font-medium uppercase text-muted-foreground">
                  Variants ({variantsQuery.data?.variants.length ?? 0})
                </div>
                {variantsQuery.isLoading ? (
                  <div className="p-4 flex justify-center">
                    <LoadingSpinner />
                  </div>
                ) : (
                  <div className="max-h-64 overflow-y-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border text-left text-xs text-muted-foreground">
                          <th className="px-3 py-2">SKU</th>
                          <th className="px-3 py-2">Color</th>
                          <th className="px-3 py-2">Size</th>
                          <th className="px-3 py-2">Stock</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(variantsQuery.data?.variants ?? []).map((v) => (
                          <tr key={v.id} className="border-b border-border last:border-0">
                            <td className="px-3 py-2 font-mono text-xs">{v.sku}</td>
                            <td className="px-3 py-2">{v.color ?? "—"}</td>
                            <td className="px-3 py-2">{v.size ?? "—"}</td>
                            <td className="px-3 py-2">{v.stock}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        Manufacturing BOM styles (e.g. STYLE-001) are separate; link optionally via Mfg style SKU on
        the template. Inventory scope only.
      </p>
    </div>
  )
}
