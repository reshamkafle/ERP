import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ExternalLink } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { ProcurementRecordFormDialog } from "@/features/procurement/ProcurementRecordFormDialog"
import {
  deleteModuleRecord,
  fetchModuleOverview,
  fetchModuleRecords,
} from "@/features/modules/modules-api"
import { useAuth } from "@/context/AuthContext"
import { keyLabelFromRecord, PROCUREMENT_MODULE_CODE } from "@/lib/procurement-record-schema"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "COMPLETED" || s === "APPROVED" || s === "RELEASED" || s === "PAID" || s === "POSTED")
    return "success"
  if (s === "IN_PROGRESS" || s === "PENDING") return "warning"
  if (s === "DRAFT" || s === "PARKED") return "secondary"
  if (s === "REJECTED" || s === "CANCELLED" || s === "BLOCKED") return "danger"
  return "default"
}

const PHASE1_FEATURES = new Set([
  "purchase_requisitions",
  "purchase_orders",
  "goods_receipt",
  "invoice_matching",
])

export function ProcurementModulePage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const featureFromUrl = searchParams.get("feature") ?? ""
  const [activeFeature, setActiveFeature] = useState<string | "all">(
    featureFromUrl || "all",
  )
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)

  useEffect(() => {
    if (featureFromUrl && PHASE1_FEATURES.has(featureFromUrl)) {
      setActiveFeature(featureFromUrl)
    }
  }, [featureFromUrl])

  const overviewQuery = useQuery({
    queryKey: ["erp-modules", PROCUREMENT_MODULE_CODE, "overview"],
    queryFn: () => fetchModuleOverview(PROCUREMENT_MODULE_CODE),
  })

  const recordsQuery = useQuery({
    queryKey: ["erp-modules", PROCUREMENT_MODULE_CODE, "records", activeFeature, search],
    queryFn: () =>
      fetchModuleRecords(PROCUREMENT_MODULE_CODE, {
        feature_code: activeFeature === "all" ? undefined : activeFeature,
        search: search || undefined,
        limit: 100,
      }),
  })

  const canWrite = canAccess(permissions, "procurement.records.write")

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteModuleRecord(PROCUREMENT_MODULE_CODE, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", PROCUREMENT_MODULE_CODE] })
      toast.success("Record deleted")
    },
    onError: () => toast.error("Could not delete record"),
  })

  const overview = overviewQuery.data
  const allRecords = recordsQuery.data?.items ?? []
  const records = allRecords.filter((r) => PHASE1_FEATURES.has(r.feature_code))

  const featureFilters = useMemo(() => {
    const feats = (overview?.features ?? []).filter((f) => PHASE1_FEATURES.has(f.code))
    return feats
  }, [overview?.features])

  const defaultFeatureCode = useMemo(() => {
    if (activeFeature !== "all") return activeFeature
    return featureFilters[0]?.code ?? "purchase_requisitions"
  }, [activeFeature, featureFilters])

  return (
    <div className="space-y-4">
      <PageHeader
        title={overview?.module_name ?? "Procurement / Purchasing"}
        description={overview?.description}
        actions={
          canWrite ? (
            <Button
              type="button"
              onClick={() => {
                setEditingId(null)
                setDialogOpen(true)
              }}
            >
              Add record
            </Button>
          ) : null
        }
      />

      <div className="flex flex-wrap gap-2">
        <Link
          to="/suppliers"
          className="inline-flex h-8 items-center rounded-md border border-input bg-background px-3 text-xs font-medium shadow-xs hover:bg-accent hover:text-accent-foreground"
        >
          <ExternalLink className="mr-1 size-3.5" aria-hidden />
          Vendor master
        </Link>
        <Link
          to="/purchases"
          className="inline-flex h-8 items-center rounded-md border border-input bg-background px-3 text-xs font-medium shadow-xs hover:bg-accent hover:text-accent-foreground"
        >
          <ExternalLink className="mr-1 size-3.5" aria-hidden />
          Quick receive & AI reorder
        </Link>
      </div>

      {overview?.integration_metrics.length ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {overview.integration_metrics.map((m) => (
            <ContentSheet key={m.label} className="p-4">
              <p className="text-xs uppercase text-muted-foreground">{m.label}</p>
              <p className="mt-1 text-lg font-semibold">{m.value}</p>
              {m.hint ? <p className="mt-0.5 text-xs text-muted-foreground">{m.hint}</p> : null}
            </ContentSheet>
          ))}
        </div>
      ) : null}

      <ContentSheet className="p-4">
        <h2 className="text-sm font-semibold">Capabilities</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          PR, PO, GRN, and invoice matching with full field sets per document.
        </p>
        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
          {featureFilters.map((f) => (
            <li key={f.code} className="text-sm">
              <span className="font-medium">{f.name}</span>
              <span className="text-muted-foreground"> — {f.description}</span>
            </li>
          ))}
        </ul>
      </ContentSheet>

      <ControlPanel className="flex flex-wrap items-center gap-2">
        <div className="flex flex-wrap gap-1">
          <FilterChip
            active={activeFeature === "all"}
            onClick={() => setActiveFeature("all")}
            label="All"
          />
          {featureFilters.map((f) => (
            <FilterChip
              key={f.code}
              active={activeFeature === f.code}
              onClick={() => setActiveFeature(f.code)}
              label={f.name}
            />
          ))}
        </div>
        <Input
          className="max-w-xs"
          placeholder="Search reference, title, party…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      <ContentSheet className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[800px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Reference</th>
                <th className="px-3 py-2 font-medium">Type</th>
                <th className="px-3 py-2 font-medium">Title</th>
                <th className="px-3 py-2 font-medium">Key ID</th>
                <th className="px-3 py-2 font-medium">Party</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium text-right">Amount</th>
                {canWrite ? (
                  <th className="px-3 py-2 font-medium text-right">Actions</th>
                ) : null}
              </tr>
            </thead>
            <tbody>
              {recordsQuery.isLoading ? (
                <tr>
                  <td
                    colSpan={canWrite ? 8 : 7}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    Loading records…
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td
                    colSpan={canWrite ? 8 : 7}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    No records for this filter.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <tr key={r.id} className="border-b border-border/60">
                    <td className="px-3 py-2 font-mono text-xs">{r.reference}</td>
                    <td className="px-3 py-2 text-xs text-muted-foreground">
                      {overview?.features.find((f) => f.code === r.feature_code)?.name ??
                        r.feature_code}
                    </td>
                    <td className="px-3 py-2">{r.title}</td>
                    <td className="px-3 py-2 font-mono text-xs text-muted-foreground">
                      {keyLabelFromRecord(r)}
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">{r.party_name ?? "—"}</td>
                    <td className="px-3 py-2">
                      <Badge variant={statusVariant(r.status)}>{r.status}</Badge>
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {r.amount != null ? Number(r.amount).toLocaleString() : "—"}
                    </td>
                    {canWrite ? (
                      <td className="px-3 py-2 text-right">
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditingId(r.id)
                            setDialogOpen(true)
                          }}
                        >
                          Edit
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="text-destructive"
                          disabled={deleteMutation.isPending}
                          onClick={() => {
                            if (window.confirm(`Delete record ${r.reference}?`)) {
                              deleteMutation.mutate(r.id)
                            }
                          }}
                        >
                          Delete
                        </Button>
                      </td>
                    ) : null}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </ContentSheet>

      <ProcurementRecordFormDialog
        open={dialogOpen}
        editingId={editingId}
        defaultFeatureCode={defaultFeatureCode}
        onClose={() => {
          setDialogOpen(false)
          setEditingId(null)
        }}
      />
    </div>
  )
}

function FilterChip({
  active,
  onClick,
  label,
}: {
  active: boolean
  onClick: () => void
  label: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
        active
          ? "bg-primary text-primary-foreground"
          : "bg-muted text-muted-foreground hover:bg-muted/80",
      )}
    >
      {label}
    </button>
  )
}
