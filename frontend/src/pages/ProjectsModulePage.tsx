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
import { ProjectsRecordFormDialog } from "@/features/projects/ProjectsRecordFormDialog"
import {
  deleteModuleRecord,
  fetchModuleOverview,
  fetchModuleRecords,
} from "@/features/modules/modules-api"
import { useAuth } from "@/context/AuthContext"
import { PROJECTS_LINKED_ROUTES, PROJECTS_PHASE1_FEATURES } from "@/lib/projects-field-groups"
import { keyLabelFromRecord, PROJECTS_MODULE_CODE } from "@/lib/projects-record-schema"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "COMPLETED" || s === "CLOSED") return "success"
  if (s === "ACTIVE" || s === "PLANNING") return "warning"
  if (s === "DRAFT") return "secondary"
  if (s === "AT_RISK" || s === "ON_HOLD") return "danger"
  if (s === "CANCELLED") return "danger"
  return "default"
}

export function ProjectsModulePage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [activeFeature, setActiveFeature] = useState<string | "all">("all")
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)

  const overviewQuery = useQuery({
    queryKey: ["erp-modules", PROJECTS_MODULE_CODE, "overview"],
    queryFn: () => fetchModuleOverview(PROJECTS_MODULE_CODE),
  })

  const recordsQuery = useQuery({
    queryKey: ["erp-modules", PROJECTS_MODULE_CODE, "records", activeFeature, search],
    queryFn: () =>
      fetchModuleRecords(PROJECTS_MODULE_CODE, {
        feature_code: activeFeature === "all" ? undefined : activeFeature,
        search: search || undefined,
        limit: 100,
      }),
  })

  const canWrite = canAccess(permissions, "projects.records.write")

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteModuleRecord(PROJECTS_MODULE_CODE, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", PROJECTS_MODULE_CODE] })
      toast.success("Project deleted")
    },
    onError: () => toast.error("Could not delete project"),
  })

  const overview = overviewQuery.data
  const allRecords = recordsQuery.data?.items ?? []
  const records = allRecords.filter((r) => PROJECTS_PHASE1_FEATURES.has(r.feature_code))

  const featureFilters = useMemo(() => {
    return (overview?.features ?? []).filter((f) => PROJECTS_PHASE1_FEATURES.has(f.code))
  }, [overview?.features])

  return (
    <div className="space-y-4">
      <PageHeader
        title={overview?.module_name ?? "Project Management"}
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
              New project
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
          Full project lifecycle: master data, planning, resources, budget, risk, execution, quality,
          documents, reporting, ERP integration, and closure.
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
          placeholder="Search reference, title, client…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      <ContentSheet className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Project code</th>
                <th className="px-3 py-2 font-medium">Project name</th>
                <th className="px-3 py-2 font-medium">Client / party</th>
                <th className="px-3 py-2 font-medium">Manager</th>
                <th className="px-3 py-2 font-medium">Start</th>
                <th className="px-3 py-2 font-medium">End</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium text-right">Budget</th>
                {canWrite ? (
                  <th className="px-3 py-2 font-medium text-right">Actions</th>
                ) : null}
              </tr>
            </thead>
            <tbody>
              {recordsQuery.isLoading ? (
                <tr>
                  <td
                    colSpan={canWrite ? 9 : 8}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    Loading projects…
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td
                    colSpan={canWrite ? 9 : 8}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    No projects for this filter.
                  </td>
                </tr>
              ) : (
                records.map((r) => {
                  const extra = (r.extra_data ?? {}) as Record<string, unknown>
                  const master = (extra.master_data ?? {}) as Record<string, unknown>
                  const manager =
                    typeof master.project_manager === "string" ? master.project_manager : "—"

                  return (
                    <tr key={r.id} className="border-b border-border/60">
                      <td className="px-3 py-2 font-mono text-xs">{keyLabelFromRecord(r)}</td>
                      <td className="px-3 py-2">{r.title}</td>
                      <td className="px-3 py-2 text-muted-foreground">{r.party_name ?? "—"}</td>
                      <td className="px-3 py-2 text-muted-foreground">{manager}</td>
                      <td className="px-3 py-2 text-muted-foreground">{r.start_date ?? "—"}</td>
                      <td className="px-3 py-2 text-muted-foreground">{r.end_date ?? "—"}</td>
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
                              if (window.confirm(`Delete project ${r.reference}?`)) {
                                deleteMutation.mutate(r.id)
                              }
                            }}
                          >
                            Delete
                          </Button>
                        </td>
                      ) : null}
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </ContentSheet>

      <ProjectsRecordFormDialog
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
    "/finance": "Finance",
    "/crm": "CRM",
    "/procurement": "Procurement",
    "/sales": "Sales",
    "/customers": "Customers",
  }

  return (
    <div className="flex flex-wrap gap-2">
      {PROJECTS_LINKED_ROUTES.map((route) => (
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
