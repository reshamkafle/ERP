import { useQuery } from "@tanstack/react-query"
import { useEffect, useMemo, useState } from "react"
import { useSearchParams } from "react-router-dom"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { BomEditor } from "@/features/bom/BomEditor"
import { BomNewDialog } from "@/features/bom/BomNewDialog"
import {
  fetchBomExplosion,
  fetchBomItems,
  fetchBomList,
  fetchBomOptional,
  fetchBomTree,
  fetchFabricSummary,
  fetchTrimSummary,
} from "@/features/bom/bom-api"
import { createEmptyBom } from "@/features/bom/bom-utils"
import { useAuth } from "@/context/AuthContext"
import { formatMoney } from "@/lib/format-money"
import type { BOMTreeNode } from "@/types/bom"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"

type TabId = "structure" | "materials" | "fabric" | "trims" | "edit"

function statusVariant(status: string) {
  if (status === "ACTIVE") return "success" as const
  if (status === "DRAFT") return "warning" as const
  if (status === "OBSOLETE") return "secondary" as const
  return "secondary" as const
}

function categoryVariant(category: string) {
  if (category === "FABRIC") return "default" as const
  if (category === "TRIM") return "secondary" as const
  if (category === "FINISHED_GOOD") return "success" as const
  if (category === "SUB_ASSEMBLY") return "warning" as const
  return "secondary" as const
}

function BomTreeView({ node, depth = 0 }: { node: BOMTreeNode; depth?: number }) {
  return (
    <li className="list-none">
      <div
        className="flex flex-wrap items-center gap-2 rounded-md border border-border bg-card px-3 py-2 text-sm"
        style={{ marginLeft: depth * 16 }}
      >
        <span className="font-medium text-foreground">{node.item.sku}</span>
        <span className="text-muted-foreground">{node.item.name}</span>
        <Badge variant={categoryVariant(node.item.category)}>{node.item.category}</Badge>
        <span className="text-muted-foreground">
          × {node.quantity_per_unit} {node.item.unit}
        </span>
        {Number(node.wastage_percentage) > 0 ? (
          <span className="text-xs text-muted-foreground">
            wastage {node.wastage_percentage}%
          </span>
        ) : null}
        {node.rolled_up_cost && Number(node.rolled_up_cost) > 0 ? (
          <span className="ml-auto tabular-nums text-foreground">
            {formatMoney(node.rolled_up_cost)}
          </span>
        ) : null}
      </div>
      {node.children.length > 0 ? (
        <ul className="mt-2 space-y-2">
          {node.children.map((child) => (
            <BomTreeView key={child.item.sku} node={child} depth={depth + 1} />
          ))}
        </ul>
      ) : null}
    </li>
  )
}

export function BomPage() {
  const { permissions } = useAuth()
  const canEdit = permissions.includes("warehouse.bom.write")
  const [searchParams, setSearchParams] = useSearchParams()
  const skuFromUrl = searchParams.get("sku") ?? ""
  const [selectedSku, setSelectedSku] = useState(skuFromUrl)
  const [orderQty, setOrderQty] = useState("100")
  const [tab, setTab] = useState<TabId>("structure")
  const [listSearch, setListSearch] = useState("")
  const [newDialogOpen, setNewDialogOpen] = useState(false)

  const qty = Math.max(1, parseInt(orderQty, 10) || 1)

  const bomListQuery = useQuery({
    queryKey: ["bom", "list"],
    queryFn: fetchBomList,
  })

  const itemsQuery = useQuery({
    queryKey: ["bom", "items"],
    queryFn: () => fetchBomItems(),
  })

  const finishedGoods = useMemo(
    () =>
      (itemsQuery.data ?? []).filter(
        (i) => i.category === "FINISHED_GOOD" || i.category === "SUB_ASSEMBLY",
      ),
    [itemsQuery.data],
  )

  const parentsWithoutBom = useMemo(() => {
    const withBom = new Set((bomListQuery.data ?? []).map((b) => b.parent_sku))
    return finishedGoods.filter((p) => !withBom.has(p.sku))
  }, [bomListQuery.data, finishedGoods])

  const filteredBomList = useMemo(() => {
    const q = listSearch.trim().toLowerCase()
    const rows = bomListQuery.data ?? []
    if (!q) return rows
    return rows.filter(
      (b) =>
        b.parent_sku.toLowerCase().includes(q) ||
        b.parent_name.toLowerCase().includes(q) ||
        b.bom_number.toLowerCase().includes(q),
    )
  }, [bomListQuery.data, listSearch])

  const filteredParentsWithoutBom = useMemo(() => {
    const q = listSearch.trim().toLowerCase()
    if (!q) return parentsWithoutBom
    return parentsWithoutBom.filter(
      (p) =>
        p.sku.toLowerCase().includes(q) ||
        p.name.toLowerCase().includes(q),
    )
  }, [parentsWithoutBom, listSearch])

  useEffect(() => {
    if (skuFromUrl && finishedGoods.some((i) => i.sku === skuFromUrl)) {
      setSelectedSku(skuFromUrl)
      return
    }
    if (!selectedSku && finishedGoods.length > 0) {
      setSelectedSku(finishedGoods[0].sku)
    }
  }, [skuFromUrl, finishedGoods, selectedSku])

  const handleSkuChange = (sku: string) => {
    setSelectedSku(sku)
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      next.set("sku", sku)
      return next
    }, { replace: true })
  }

  const openBom = (sku: string, editTab = false) => {
    handleSkuChange(sku)
    if (editTab && canEdit) setTab("edit")
    else setTab("structure")
  }

  const bomQuery = useQuery({
    queryKey: ["bom", "detail", selectedSku],
    queryFn: () => fetchBomOptional(selectedSku),
    enabled: Boolean(selectedSku),
  })

  const selectedParent = finishedGoods.find((i) => i.sku === selectedSku)
  const isCreating =
    Boolean(selectedParent) &&
    bomQuery.data === null &&
    !bomQuery.isLoading &&
    !bomQuery.isFetching

  const editBom =
    bomQuery.data ?? (isCreating && selectedParent ? createEmptyBom(selectedParent) : null)

  const treeQuery = useQuery({
    queryKey: ["bom", "tree", selectedSku],
    queryFn: () => fetchBomTree(selectedSku),
    enabled: Boolean(selectedSku) && Boolean(bomQuery.data) && tab === "structure",
  })

  const explosionQuery = useQuery({
    queryKey: ["bom", "explode", selectedSku, qty],
    queryFn: () => fetchBomExplosion(selectedSku, qty),
    enabled: Boolean(selectedSku) && Boolean(bomQuery.data) && tab === "materials",
  })

  const fabricQuery = useQuery({
    queryKey: ["bom", "fabric", selectedSku, qty],
    queryFn: () => fetchFabricSummary(selectedSku, qty),
    enabled: Boolean(selectedSku) && Boolean(bomQuery.data) && tab === "fabric",
  })

  const trimQuery = useQuery({
    queryKey: ["bom", "trim", selectedSku, qty],
    queryFn: () => fetchTrimSummary(selectedSku, qty),
    enabled: Boolean(selectedSku) && Boolean(bomQuery.data) && tab === "trims",
  })

  const tabs: { id: TabId; label: string }[] = [
    { id: "structure", label: "BOM structure" },
    { id: "materials", label: "Material requirements" },
    { id: "fabric", label: "Fabric consumption" },
    { id: "trims", label: "Trim requirements" },
    ...(canEdit ? [{ id: "edit" as const, label: isCreating ? "Create BOM" : "Edit BOM" }] : []),
  ]

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <PageHeader
        title="Bill of Materials"
        description="Multi-level BOM for garment manufacturing — fabrics, trims, consumption, and wastage."
        actions={
          canEdit ? (
            <Button
              type="button"
              onClick={() => setNewDialogOpen(true)}
            >
              New BOM
            </Button>
          ) : undefined
        }
      />

      <ControlPanel>
        <Input
          className="max-w-md"
          placeholder="Search BOM number, parent SKU, name…"
          value={listSearch}
          onChange={(e) => setListSearch(e.target.value)}
        />
      </ControlPanel>

      <ContentSheet className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[800px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Parent SKU</th>
                <th className="px-3 py-2 font-medium">Name</th>
                <th className="px-3 py-2 font-medium">BOM number</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Version</th>
                <th className="px-3 py-2 font-medium">Lines</th>
                {canEdit ? (
                  <th className="px-3 py-2 font-medium text-right">Actions</th>
                ) : null}
              </tr>
            </thead>
            <tbody>
              {bomListQuery.isLoading ? (
                <tr>
                  <td
                    colSpan={canEdit ? 7 : 6}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    Loading BOMs…
                  </td>
                </tr>
              ) : filteredBomList.length === 0 ? (
                <tr>
                  <td
                    colSpan={canEdit ? 7 : 6}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    {listSearch
                      ? "No BOMs match your search."
                      : "No BOMs yet. Create one for a finished good or sub-assembly."}
                  </td>
                </tr>
              ) : (
                filteredBomList.map((row) => (
                  <tr
                    key={row.parent_sku}
                    className={`border-b border-border last:border-0 ${
                      row.parent_sku === selectedSku ? "bg-muted/40" : ""
                    }`}
                  >
                    <td className="px-3 py-2 font-mono text-xs">{row.parent_sku}</td>
                    <td className="px-3 py-2">
                      <button
                        type="button"
                        className="font-medium text-primary hover:underline"
                        onClick={() => openBom(row.parent_sku)}
                      >
                        {row.parent_name}
                      </button>
                    </td>
                    <td className="px-3 py-2 font-mono text-xs">{row.bom_number}</td>
                    <td className="px-3 py-2">
                      <Badge variant={statusVariant(row.status)}>{row.status}</Badge>
                    </td>
                    <td className="px-3 py-2 tabular-nums">v{row.version}</td>
                    <td className="px-3 py-2 tabular-nums">{row.line_count}</td>
                    {canEdit ? (
                      <td className="px-3 py-2 text-right">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => openBom(row.parent_sku, true)}
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
        {canEdit && filteredParentsWithoutBom.length > 0 ? (
          <div className="border-t border-border bg-muted/20 px-3 py-3">
            <p className="text-xs font-medium uppercase text-muted-foreground">
              Styles without BOM ({filteredParentsWithoutBom.length})
            </p>
            <ul className="mt-2 space-y-1">
              {filteredParentsWithoutBom.map((item) => (
                <li
                  key={item.sku}
                  className="flex flex-wrap items-center justify-between gap-2 text-sm"
                >
                  <button
                    type="button"
                    className="text-left text-primary hover:underline"
                    onClick={() => openBom(item.sku)}
                  >
                    <span className="font-mono text-xs">{item.sku}</span>
                    <span className="ml-2 text-foreground">{item.name}</span>
                  </button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => openBom(item.sku, true)}
                  >
                    Create BOM
                  </Button>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </ContentSheet>

      <ControlPanel className="flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium text-foreground" htmlFor="bom-sku">
            Parent item (style / assembly)
          </label>
          <Select
            id="bom-sku"
            value={selectedSku}
            onChange={(e) => handleSkuChange(e.target.value)}
          >
            {finishedGoods.map((item) => (
              <option key={item.sku} value={item.sku}>
                {item.sku} — {item.name} ({item.category})
              </option>
            ))}
          </Select>
        </div>
        <div className="w-full space-y-2 sm:w-40">
          <label className="text-sm font-medium text-foreground" htmlFor="bom-qty">
            Order quantity
          </label>
          <Input
            id="bom-qty"
            type="number"
            min={1}
            value={orderQty}
            onChange={(e) => setOrderQty(e.target.value)}
          />
        </div>
      </ControlPanel>

      <ContentSheet className="space-y-4">
        {bomQuery.isLoading ? (
          <p className="text-sm text-muted-foreground">Loading BOM…</p>
        ) : bomQuery.data ? (
          <div className="rounded-lg border border-border bg-muted/30 px-4 py-3 text-sm">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-medium text-foreground">{bomQuery.data.parent_name}</span>
              <Badge variant="secondary">{bomQuery.data.bom_number}</Badge>
              <Badge variant={statusVariant(bomQuery.data.status)}>{bomQuery.data.status}</Badge>
              <Badge variant="secondary">{bomQuery.data.bom_type}</Badge>
            </div>
            <p className="mt-1 text-muted-foreground">
              {bomQuery.data.parent_sku} · v{bomQuery.data.version} ·{" "}
              {bomQuery.data.lines.length} direct component
              {bomQuery.data.lines.length === 1 ? "" : "s"}
              {bomQuery.data.eco_number ? ` · ECO ${bomQuery.data.eco_number}` : ""}
              {bomQuery.data.effective_start_date
                ? ` · effective ${bomQuery.data.effective_start_date}`
                : ""}
            </p>
          </div>
        ) : isCreating && selectedParent ? (
          <div className="rounded-lg border border-dashed border-border bg-muted/20 px-4 py-3 text-sm">
            <p className="font-medium text-foreground">No BOM for {selectedParent.sku}</p>
            <p className="mt-1 text-muted-foreground">
              {selectedParent.name} does not have a bill of materials yet. Open the{" "}
              <strong>Create BOM</strong> tab to add components.
            </p>
            {canEdit ? (
              <Button
                type="button"
                className="mt-3"
                size="sm"
                onClick={() => setTab("edit")}
              >
                Create BOM
              </Button>
            ) : null}
          </div>
        ) : bomQuery.isError ? (
          <p className="text-sm text-destructive">Could not load BOM for this item.</p>
        ) : null}

        <div className="flex flex-wrap gap-2 border-b border-border pb-2">
          {tabs.map((t) => (
            <Button
              key={t.id}
              type="button"
              variant={tab === t.id ? "default" : "outline"}
              size="sm"
              onClick={() => setTab(t.id)}
              disabled={t.id !== "edit" && !bomQuery.data}
            >
              {t.label}
            </Button>
          ))}
        </div>

        {tab === "structure" ? (
          <section className="space-y-3">
            {treeQuery.isLoading ? (
              <p className="text-sm text-muted-foreground">Loading BOM tree…</p>
            ) : treeQuery.isError ? (
              <p className="text-sm text-destructive">No BOM tree for this item.</p>
            ) : treeQuery.data ? (
              <ul className="space-y-2">
                <BomTreeView node={treeQuery.data.root} />
              </ul>
            ) : null}
            {bomQuery.data && bomQuery.data.lines.length > 0 ? (
              <div className="mt-6 overflow-x-auto rounded-xl border border-border">
                <table className="w-full min-w-[640px] text-left text-sm">
                  <thead className="border-b border-border bg-muted/50 text-muted-foreground">
                    <tr>
                      <th className="px-3 py-2 font-medium">Component</th>
                      <th className="px-3 py-2 font-medium">Category</th>
                      <th className="px-3 py-2 font-medium">Qty / unit</th>
                      <th className="px-3 py-2 font-medium">Consumption</th>
                      <th className="px-3 py-2 font-medium">Wastage %</th>
                      <th className="px-3 py-2 font-medium">Supplier</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bomQuery.data.lines.map((line) => (
                      <tr
                        key={line.component_sku}
                        className="border-b border-border last:border-0"
                      >
                        <td className="px-3 py-2">
                          <span className="font-medium">{line.component_sku}</span>
                          <span className="ml-2 text-muted-foreground">{line.component_name}</span>
                        </td>
                        <td className="px-3 py-2">
                          <Badge variant={categoryVariant(line.component_category)}>
                            {line.component_category}
                          </Badge>
                        </td>
                        <td className="px-3 py-2 tabular-nums">{line.quantity_per_unit}</td>
                        <td className="px-3 py-2">{line.consumption_type}</td>
                        <td className="px-3 py-2 tabular-nums">{line.wastage_percentage}</td>
                        <td className="px-3 py-2 text-muted-foreground">
                          {line.product_snapshot?.default_supplier_name ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </section>
        ) : null}

        {tab === "materials" ? (
          <section>
            {explosionQuery.isLoading ? (
              <p className="text-sm text-muted-foreground">Calculating requirements…</p>
            ) : explosionQuery.data ? (
              <>
                <p className="mb-4 text-sm text-muted-foreground">
                  Total material cost for {explosionQuery.data.order_quantity} units:{" "}
                  <span className="font-semibold text-foreground">
                    {formatMoney(explosionQuery.data.total_material_cost)}
                  </span>
                </p>
                <div className="overflow-x-auto rounded-xl border border-border">
                  <table className="w-full min-w-[720px] text-left text-sm">
                    <thead className="border-b border-border bg-muted/50 text-muted-foreground">
                      <tr>
                        <th className="px-3 py-2 font-medium">SKU</th>
                        <th className="px-3 py-2 font-medium">Name</th>
                        <th className="px-3 py-2 font-medium">Category</th>
                        <th className="px-3 py-2 font-medium">Gross</th>
                        <th className="px-3 py-2 font-medium">Wastage</th>
                        <th className="px-3 py-2 font-medium">Total</th>
                        <th className="px-3 py-2 font-medium">Cost</th>
                      </tr>
                    </thead>
                    <tbody>
                      {explosionQuery.data.lines.map((line) => (
                        <tr key={line.sku} className="border-b border-border last:border-0">
                          <td className="px-3 py-2 font-medium">{line.sku}</td>
                          <td className="px-3 py-2">{line.name}</td>
                          <td className="px-3 py-2">
                            <Badge variant={categoryVariant(line.category)}>{line.category}</Badge>
                          </td>
                          <td className="px-3 py-2 tabular-nums">
                            {line.gross_qty} {line.unit}
                          </td>
                          <td className="px-3 py-2 tabular-nums">
                            {line.wastage_qty} {line.unit}
                          </td>
                          <td className="px-3 py-2 tabular-nums font-medium">
                            {line.total_qty} {line.unit}
                          </td>
                          <td className="px-3 py-2 tabular-nums">
                            {formatMoney(line.extended_cost)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : null}
          </section>
        ) : null}

        {tab === "fabric" && fabricQuery.data ? (
          <section className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Total fabric:{" "}
              <span className="font-medium text-foreground">
                {fabricQuery.data.total_meters} meters
              </span>
              {" · "}
              Cost: {formatMoney(fabricQuery.data.total_fabric_cost)}
            </p>
            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-border bg-muted/50 text-muted-foreground">
                  <tr>
                    <th className="px-3 py-2 font-medium">Fabric</th>
                    <th className="px-3 py-2 font-medium">Gross</th>
                    <th className="px-3 py-2 font-medium">Wastage</th>
                    <th className="px-3 py-2 font-medium">Total</th>
                    <th className="px-3 py-2 font-medium">Wastage %</th>
                    <th className="px-3 py-2 font-medium">Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {fabricQuery.data.fabrics.map((f) => (
                    <tr key={f.sku} className="border-b border-border last:border-0">
                      <td className="px-3 py-2">
                        <span className="font-medium">{f.sku}</span>
                        <span className="ml-2 text-muted-foreground">{f.name}</span>
                      </td>
                      <td className="px-3 py-2 tabular-nums">
                        {f.gross_qty} {f.unit}
                      </td>
                      <td className="px-3 py-2 tabular-nums">
                        {f.wastage_qty} {f.unit}
                      </td>
                      <td className="px-3 py-2 tabular-nums font-medium">
                        {f.total_qty} {f.unit}
                      </td>
                      <td className="px-3 py-2 tabular-nums">{f.wastage_percentage}%</td>
                      <td className="px-3 py-2 tabular-nums">{formatMoney(f.extended_cost)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {tab === "edit" && canEdit && editBom ? (
          <BomEditor
            parentSku={selectedSku}
            bom={editBom}
            isNew={isCreating}
            onCancel={() => setTab("structure")}
            onSaved={() => {
              void bomQuery.refetch()
              void bomListQuery.refetch()
            }}
          />
        ) : null}

        {tab === "trims" && trimQuery.data ? (
          <section className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Total trim cost: {formatMoney(trimQuery.data.total_trim_cost)}
            </p>
            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-border bg-muted/50 text-muted-foreground">
                  <tr>
                    <th className="px-3 py-2 font-medium">Trim</th>
                    <th className="px-3 py-2 font-medium">Gross</th>
                    <th className="px-3 py-2 font-medium">Wastage</th>
                    <th className="px-3 py-2 font-medium">Total</th>
                    <th className="px-3 py-2 font-medium">Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {trimQuery.data.trims.map((t) => (
                    <tr key={t.sku} className="border-b border-border last:border-0">
                      <td className="px-3 py-2">
                        <span className="font-medium">{t.sku}</span>
                        <span className="ml-2 text-muted-foreground">{t.name}</span>
                      </td>
                      <td className="px-3 py-2 tabular-nums">
                        {t.gross_qty} {t.unit}
                      </td>
                      <td className="px-3 py-2 tabular-nums">
                        {t.wastage_qty} {t.unit}
                      </td>
                      <td className="px-3 py-2 tabular-nums font-medium">
                        {t.total_qty} {t.unit}
                      </td>
                      <td className="px-3 py-2 tabular-nums">{formatMoney(t.extended_cost)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}
      </ContentSheet>

      {canEdit ? (
        <BomNewDialog
          open={newDialogOpen}
          parents={finishedGoods}
          existingBoms={bomListQuery.data ?? []}
          onClose={() => setNewDialogOpen(false)}
          onSelect={(sku) => {
            setNewDialogOpen(false)
            openBom(sku, true)
          }}
        />
      ) : null}
    </div>
    </PosOnlyRedirect>
  )
}