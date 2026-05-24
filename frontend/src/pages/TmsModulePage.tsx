import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ExternalLink } from "lucide-react"
import { useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { TmsRecordFormDialog } from "@/features/tms/TmsRecordFormDialog"
import {
  deleteModuleRecord,
  fetchModuleOverview,
  fetchModuleRecords,
} from "@/features/modules/modules-api"
import { useAuth } from "@/context/AuthContext"
import { TMS_LINKED_ROUTES, TMS_PHASE1_FEATURES } from "@/lib/tms-field-groups"
import { keyLabelFromRecord, TMS_MODULE_CODE } from "@/lib/tms-record-schema"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "DELIVERED") return "success"
  if (s === "IN_TRANSIT" || s === "TENDERED") return "warning"
  if (s === "PLANNED") return "secondary"
  if (s === "EXCEPTION" || s === "CANCELLED") return "danger"
  return "default"
}

export function TmsModulePage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [activeFeature, setActiveFeature] = useState<string | "all">("all")
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)

  const overviewQuery = useQuery({
    queryKey: ["erp-modules", TMS_MODULE_CODE, "overview"],
    queryFn: () => fetchModuleOverview(TMS_MODULE_CODE),
  })

  const recordsQuery = useQuery({
    queryKey: ["erp-modules", TMS_MODULE_CODE, "records", activeFeature, search],
    queryFn: () =>
      fetchModuleRecords(TMS_MODULE_CODE, {
        feature_code: activeFeature === "all" ? undefined : activeFeature,
        search: search || undefined,
        limit: 100,
      }),
  })

  const canWrite = canAccess(permissions, "tms.records.write")

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteModuleRecord(TMS_MODULE_CODE, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", TMS_MODULE_CODE] })
      toast.success("Shipment deleted")
    },
    onError: () => toast.error("Could not delete shipment"),
  })

  const overview = overviewQuery.data
  const allRecords = recordsQuery.data?.items ?? []
  const records = allRecords.filter((r) => TMS_PHASE1_FEATURES.has(r.feature_code))

  const featureFilters = useMemo(() => {
    return (overview?.features ?? []).filter((f) => TMS_PHASE1_FEATURES.has(f.code))
  }, [overview?.features])

  return (
    <div className="space-y-4">
      <PageHeader
        title={overview?.module_name ?? "Transportation Management System"}
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
              New shipment
            </Button>
          ) : null
        }
      />

      <LinkedRoutes />

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
          Full shipment lifecycle: origin, destination, line items, carrier rating, compliance, tracking, and freight audit.
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
          placeholder="Search reference, title, carrier…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      <ContentSheet className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Shipment ID</th>
                <th className="px-3 py-2 font-medium">Title</th>
                <th className="px-3 py-2 font-medium">Tracking #</th>
                <th className="px-3 py-2 font-medium">Carrier / Party</th>
                <th className="px-3 py-2 font-medium">Ship date</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium text-right">Freight</th>
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
                    Loading shipments…
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td
                    colSpan={canWrite ? 8 : 7}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    No shipments for this filter.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <tr key={r.id} className="border-b border-border/60">
                    <td className="px-3 py-2 font-mono text-xs">{r.reference}</td>
                    <td className="px-3 py-2">{r.title}</td>
                    <td className="px-3 py-2 font-mono text-xs text-muted-foreground">
                      {keyLabelFromRecord(r)}
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">{r.party_name ?? "—"}</td>
                    <td className="px-3 py-2 text-muted-foreground">{r.start_date ?? "—"}</td>
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
                            if (window.confirm(`Delete shipment ${r.reference}?`)) {
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

      <TmsRecordFormDialog
        open={dialogOpen}
        editingId={editingId}
        onClose={() => {
          setDialogOpen(false)
          setEditingId(null)
        }}
      />
    </div>
  )
}

function LinkedRoutes() {
  const labels: Record<string, string> = {
    "/sales": "Sales orders",
    "/warehouse": "Warehouse",
    "/customers": "Customers",
    "/inventory": "Inventory",
  }

  return (
    <div className="flex flex-wrap gap-2">
      {TMS_LINKED_ROUTES.map((route) => (
        <Link
          key={route}
          to={route}
          className="inline-flex h-8 items-center rounded-md border border-input bg-background px-3 text-xs font-medium shadow-xs hover:bg-accent hover:text-accent-foreground"
        >
          <ExternalLink className="mr-1 size-3.5" aria-hidden />
          {labels[route] ?? route}
        </Link>
      ))}
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
