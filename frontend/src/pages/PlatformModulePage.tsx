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
import { PlatformRecordFormDialog } from "@/features/platform/PlatformRecordFormDialog"
import {
  deleteModuleRecord,
  fetchModuleOverview,
  fetchModuleRecords,
} from "@/features/modules/modules-api"
import { useAuth } from "@/context/AuthContext"
import { PLATFORM_LINKED_ROUTES } from "@/lib/platform-field-groups"
import {
  featureLabelFromCode,
  keyLabelFromRecord,
  PLATFORM_MODULE_CODE,
} from "@/lib/platform-record-schema"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "LIVE" || s === "APPROVED") return "success"
  if (s === "IN_IMPLEMENTATION" || s === "IN_REVIEW") return "warning"
  if (s === "DRAFT") return "secondary"
  if (s === "RETIRED") return "danger"
  return "default"
}

export function PlatformModulePage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [activeFeature, setActiveFeature] = useState<string | "all">("all")
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)

  const overviewQuery = useQuery({
    queryKey: ["erp-modules", PLATFORM_MODULE_CODE, "overview"],
    queryFn: () => fetchModuleOverview(PLATFORM_MODULE_CODE),
  })

  const recordsQuery = useQuery({
    queryKey: ["erp-modules", PLATFORM_MODULE_CODE, "records", activeFeature, search],
    queryFn: () =>
      fetchModuleRecords(PLATFORM_MODULE_CODE, {
        feature_code: activeFeature === "all" ? undefined : activeFeature,
        search: search || undefined,
        limit: 100,
      }),
  })

  const canWrite = canAccess(permissions, "platform.records.write")

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteModuleRecord(PLATFORM_MODULE_CODE, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", PLATFORM_MODULE_CODE] })
      toast.success("Module record deleted")
    },
    onError: () => toast.error("Could not delete module record"),
  })

  const overview = overviewQuery.data
  const records = recordsQuery.data?.items ?? []

  const defaultFeatureCode = useMemo(() => {
    if (activeFeature !== "all") return activeFeature
    return overview?.features[0]?.code ?? "business_intelligence"
  }, [activeFeature, overview?.features])

  return (
    <div className="space-y-4">
      <PageHeader
        title={overview?.module_name ?? "Additional / Industry-Specific Modules"}
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
          Document industry-specific modules with requirements for features, compliance, integration,
          implementation, and ROI.
        </p>
        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
          {(overview?.features ?? []).map((f) => (
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
          {(overview?.features ?? []).map((f) => (
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
          placeholder="Search reference, title, industry…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      <ContentSheet className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Reference</th>
                <th className="px-3 py-2 font-medium">Module name</th>
                <th className="px-3 py-2 font-medium">Feature</th>
                <th className="px-3 py-2 font-medium">Industry</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium text-right">Est. cost</th>
                {canWrite ? (
                  <th className="px-3 py-2 font-medium text-right">Actions</th>
                ) : null}
              </tr>
            </thead>
            <tbody>
              {recordsQuery.isLoading ? (
                <tr>
                  <td
                    colSpan={canWrite ? 7 : 6}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    Loading records…
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td
                    colSpan={canWrite ? 7 : 6}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    No industry module records for this filter.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <tr key={r.id} className="border-b border-border/60">
                    <td className="px-3 py-2 font-mono text-xs">{r.reference}</td>
                    <td className="px-3 py-2">{r.title}</td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {featureLabelFromCode(r.feature_code)}
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">{keyLabelFromRecord(r)}</td>
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

      <PlatformRecordFormDialog
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

function LinkedRoutes() {
  const labels: Record<string, string> = {
    "/reports": "Reports",
    "/pos": "Point of Sale",
  }

  return (
    <div className="flex flex-wrap gap-2">
      {PLATFORM_LINKED_ROUTES.map((route) => (
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
