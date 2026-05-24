import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useMemo, useState } from "react"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { HcmRecordFormDialog } from "@/features/hcm/HcmRecordFormDialog"
import {
  deleteModuleRecord,
  fetchModuleOverview,
  fetchModuleRecords,
} from "@/features/modules/modules-api"
import { useAuth } from "@/context/AuthContext"
import {
  benefitsEnrollmentFromRecord,
  benefitsPlanFromRecord,
  departmentFromRecord,
  employeeIdFromRecord,
  fullNameFromRecord,
  HCM_MODULE_CODE,
  managerFromRecord,
  payPeriodFromRecord,
  payrollEmployeeFromRecord,
  performanceEmployeeFromRecord,
  performanceRatingFromRecord,
  recruitmentCandidateFromRecord,
  recruitmentRequisitionFromRecord,
  recruitmentStageFromRecord,
  timeEmployeeFromRecord,
  timePeriodFromRecord,
  trainingCourseFromRecord,
  trainingStatusFromRecord,
} from "@/lib/hcm-record-schema"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"
import type { ModuleRecord } from "@/types/module"

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "COMPLETED" || s === "APPROVED") return "success"
  if (s === "IN_PROGRESS" || s === "ACTIVE") return "default"
  if (s === "DRAFT" || s === "ON_LEAVE") return "secondary"
  if (s === "REJECTED" || s === "CANCELLED" || s === "TERMINATED") return "danger"
  if (s === "RETIRED") return "warning"
  return "warning"
}

type ColumnDef = {
  key: string
  header: string
  cell: (r: ModuleRecord) => React.ReactNode
  className?: string
}

function columnsForFeature(
  feature: string | "all",
  overviewFeatures: { code: string; name: string }[],
): ColumnDef[] {
  const featureName = (code: string) =>
    overviewFeatures.find((f) => f.code === code)?.name ?? code

  const base: ColumnDef[] = [
    {
      key: "reference",
      header: "Reference",
      cell: (r) => <span className="font-mono text-xs">{r.reference}</span>,
    },
    {
      key: "feature",
      header: "Feature",
      cell: (r) => (
        <span className="text-xs text-muted-foreground">{featureName(r.feature_code)}</span>
      ),
    },
  ]

  if (feature === "employee_records") {
    return [
      ...base,
      { key: "emp_id", header: "Employee ID", cell: (r) => employeeIdFromRecord(r) },
      { key: "name", header: "Full name", cell: (r) => fullNameFromRecord(r) },
      { key: "dept", header: "Department", cell: (r) => departmentFromRecord(r) },
      {
        key: "status",
        header: "Status",
        cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
      },
      {
        key: "hire",
        header: "Hire date",
        cell: (r) => r.start_date ?? "—",
        className: "text-muted-foreground",
      },
      { key: "mgr", header: "Manager", cell: (r) => managerFromRecord(r) },
    ]
  }

  if (feature === "payroll") {
    return [
      ...base,
      { key: "emp", header: "Employee", cell: (r) => payrollEmployeeFromRecord(r) },
      { key: "period", header: "Pay period", cell: (r) => payPeriodFromRecord(r) },
      {
        key: "gross",
        header: "Gross",
        cell: (r) => (
          <span className="tabular-nums">
            {r.amount != null ? Number(r.amount).toLocaleString() : "—"}
          </span>
        ),
        className: "text-right",
      },
      {
        key: "status",
        header: "Status",
        cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
      },
    ]
  }

  if (feature === "recruitment") {
    return [
      ...base,
      {
        key: "req",
        header: "Requisition",
        cell: (r) => recruitmentRequisitionFromRecord(r),
      },
      { key: "candidate", header: "Candidate", cell: (r) => recruitmentCandidateFromRecord(r) },
      { key: "stage", header: "Stage", cell: (r) => recruitmentStageFromRecord(r) },
      {
        key: "status",
        header: "Status",
        cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
      },
    ]
  }

  if (feature === "performance") {
    return [
      ...base,
      { key: "title", header: "Title", cell: (r) => r.title },
      { key: "emp", header: "Employee", cell: (r) => performanceEmployeeFromRecord(r) },
      { key: "rating", header: "Rating", cell: (r) => performanceRatingFromRecord(r) },
      {
        key: "status",
        header: "Status",
        cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
      },
    ]
  }

  if (feature === "training") {
    return [
      ...base,
      { key: "course", header: "Course", cell: (r) => trainingCourseFromRecord(r) },
      { key: "completion", header: "Completion", cell: (r) => trainingStatusFromRecord(r) },
      {
        key: "status",
        header: "Status",
        cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
      },
    ]
  }

  if (feature === "time_attendance") {
    return [
      ...base,
      { key: "emp", header: "Employee", cell: (r) => timeEmployeeFromRecord(r) },
      { key: "period", header: "Period", cell: (r) => timePeriodFromRecord(r) },
      {
        key: "status",
        header: "Status",
        cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
      },
    ]
  }

  if (feature === "benefits") {
    return [
      ...base,
      { key: "plan", header: "Health plan", cell: (r) => benefitsPlanFromRecord(r) },
      {
        key: "enrollment",
        header: "Enrollment",
        cell: (r) => benefitsEnrollmentFromRecord(r),
      },
      {
        key: "status",
        header: "Status",
        cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
      },
    ]
  }

  return [
    ...base,
    { key: "title", header: "Title", cell: (r) => r.title },
    {
      key: "status",
      header: "Status",
      cell: (r) => <Badge variant={statusVariant(r.status)}>{r.status}</Badge>,
    },
  ]
}

export function HcmModulePage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [activeFeature, setActiveFeature] = useState<string | "all">("all")
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)

  const overviewQuery = useQuery({
    queryKey: ["erp-modules", HCM_MODULE_CODE, "overview"],
    queryFn: () => fetchModuleOverview(HCM_MODULE_CODE),
  })

  const recordsQuery = useQuery({
    queryKey: ["erp-modules", HCM_MODULE_CODE, "records", activeFeature, search],
    queryFn: () =>
      fetchModuleRecords(HCM_MODULE_CODE, {
        feature_code: activeFeature === "all" ? undefined : activeFeature,
        search: search || undefined,
        limit: 100,
      }),
  })

  const canWrite = canAccess(permissions, "hcm.records.write")

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteModuleRecord(HCM_MODULE_CODE, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", HCM_MODULE_CODE] })
      toast.success("Record deleted")
    },
    onError: () => toast.error("Could not delete record"),
  })

  const overview = overviewQuery.data
  const records = recordsQuery.data?.items ?? []
  const features = overview?.features ?? []

  const defaultFeatureCode = useMemo(() => {
    if (activeFeature !== "all") return activeFeature
    return features[0]?.code ?? "employee_records"
  }, [activeFeature, features])

  const columns = useMemo(
    () => columnsForFeature(activeFeature, features),
    [activeFeature, features],
  )

  const searchPlaceholder =
    activeFeature === "employee_records"
      ? "Search employee ID, name, department…"
      : "Search reference, title, party…"

  const colSpan = columns.length + (canWrite ? 1 : 0)

  return (
    <div className="space-y-4">
      <PageHeader
        title={overview?.module_name ?? "Human Capital Management (HCM) / HR"}
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
          {overview?.total_records ?? 0} records across {features.length} feature areas
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setActiveFeature("all")}
            className={cn(
              "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
              activeFeature === "all"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80",
            )}
          >
            All
          </button>
          {features.map((f) => (
            <button
              key={f.code}
              type="button"
              onClick={() => setActiveFeature(f.code)}
              className={cn(
                "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                activeFeature === f.code
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80",
              )}
              title={f.description}
            >
              {f.name}
              <span className="ml-1 opacity-70">({f.record_count})</span>
            </button>
          ))}
        </div>
      </ContentSheet>

      <ControlPanel>
        <Input
          className="max-w-md"
          placeholder={searchPlaceholder}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      <ContentSheet className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className={cn(
                      "px-3 py-2 font-medium",
                      col.className?.includes("text-right") ? "text-right" : "",
                    )}
                  >
                    {col.header}
                  </th>
                ))}
                {canWrite ? (
                  <th className="px-3 py-2 font-medium text-right">Actions</th>
                ) : null}
              </tr>
            </thead>
            <tbody>
              {recordsQuery.isLoading ? (
                <tr>
                  <td colSpan={colSpan} className="px-3 py-8 text-center text-muted-foreground">
                    Loading records…
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={colSpan} className="px-3 py-8 text-center text-muted-foreground">
                    No records for this filter.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <tr key={r.id} className="border-b border-border/60">
                    {columns.map((col) => (
                      <td
                        key={col.key}
                        className={cn("px-3 py-2", col.className)}
                      >
                        {col.cell(r)}
                      </td>
                    ))}
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

      <HcmRecordFormDialog
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
