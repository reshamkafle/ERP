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
import {
  createModuleRecord,
  deleteModuleRecord,
  fetchModuleOverview,
  fetchModuleRecords,
} from "@/features/modules/modules-api"
import { useAuth } from "@/context/AuthContext"
import { canAccess } from "@/lib/permissions"
import { MODULE_CODE_BY_ROUTE } from "@/lib/module-meta"
import { cn } from "@/lib/utils"

type ModuleHubPageProps = {
  routePath: string
}

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "COMPLETED" || s === "APPROVED") return "success"
  if (s === "IN_PROGRESS" || s === "ACTIVE") return "default"
  if (s === "DRAFT") return "secondary"
  if (s === "REJECTED" || s === "CANCELLED") return "danger"
  return "warning"
}

export function ModuleHubPage({ routePath }: ModuleHubPageProps) {
  const moduleCode = MODULE_CODE_BY_ROUTE[routePath]
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [activeFeature, setActiveFeature] = useState<string | "all">("all")
  const [search, setSearch] = useState("")
  const [newTitle, setNewTitle] = useState("")

  const overviewQuery = useQuery({
    queryKey: ["erp-modules", moduleCode, "overview"],
    queryFn: () => fetchModuleOverview(moduleCode),
    enabled: Boolean(moduleCode),
  })

  const recordsQuery = useQuery({
    queryKey: ["erp-modules", moduleCode, "records", activeFeature, search],
    queryFn: () =>
      fetchModuleRecords(moduleCode, {
        feature_code: activeFeature === "all" ? undefined : activeFeature,
        search: search || undefined,
        limit: 100,
      }),
    enabled: Boolean(moduleCode),
  })

  const writePermission = useMemo(() => {
    const map: Record<string, string> = {
      finance: "finance.records.write",
      hcm: "hcm.records.write",
      procurement: "procurement.records.write",
      warehouse: "warehouse.ops.write",
      scm: "scm.records.write",
      manufacturing: "manufacturing.ops.write",
      sales: "sales.dist.write",
      crm: "crm.records.write",
      projects: "projects.records.write",
      platform: "platform.records.write",
    }
    return map[moduleCode] ?? ""
  }, [moduleCode])

  const canWrite = canAccess(permissions, writePermission)

  const createMutation = useMutation({
    mutationFn: () => {
      const feature =
        activeFeature !== "all"
          ? activeFeature
          : (overviewQuery.data?.features[0]?.code ?? "general_ledger")
      const ref = `MAN-${Date.now().toString(36).toUpperCase()}`
      return createModuleRecord(moduleCode, {
        feature_code: feature,
        reference: ref,
        title: newTitle.trim() || `New ${feature} record`,
        status: "DRAFT",
      })
    },
    onSuccess: () => {
      setNewTitle("")
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", moduleCode] })
      toast.success("Record created")
    },
    onError: () => toast.error("Could not create record"),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteModuleRecord(moduleCode, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", moduleCode] })
      toast.success("Record deleted")
    },
    onError: () => toast.error("Could not delete record"),
  })

  const overview = overviewQuery.data
  const records = recordsQuery.data?.items ?? []

  const linkedRoutes: { label: string; to: string }[] = useMemo(() => {
    const map: Record<string, { label: string; to: string }> = {
      "/inventory": { label: "Inventory", to: "/inventory" },
      "/warehouses": { label: "Warehouses", to: "/warehouses" },
      "/locations": { label: "Locations", to: "/locations" },
      "/bom": { label: "BOM", to: "/bom" },
      "/suppliers": { label: "Suppliers", to: "/suppliers" },
      "/purchases": { label: "Purchases", to: "/purchases" },
      "/customers": { label: "Customers", to: "/customers" },
      "/sales": { label: "Sales", to: "/sales" },
      "/pos": { label: "POS", to: "/pos" },
      "/promotions": { label: "Promotions", to: "/promotions" },
      "/reports": { label: "Reports", to: "/reports" },
    }
    if (!overview) return []
    const catalog = [
      "/inventory",
      "/warehouses",
      "/locations",
      "/bom",
      "/suppliers",
      "/purchases",
      "/customers",
      "/sales",
      "/pos",
      "/promotions",
      "/reports",
    ]
    return catalog
      .filter((r) => {
        if (moduleCode === "finance" || moduleCode === "platform") return r === "/reports"
        if (moduleCode === "procurement") return ["/suppliers", "/purchases"].includes(r)
        if (moduleCode === "warehouse")
          return ["/inventory", "/warehouses", "/locations", "/bom"].includes(r)
        if (moduleCode === "manufacturing") return r === "/bom"
        if (moduleCode === "sales") return ["/sales", "/pos", "/promotions"].includes(r)
        if (moduleCode === "crm") return r === "/customers"
        return false
      })
      .map((r) => map[r])
      .filter(Boolean)
  }, [moduleCode, overview])

  if (!moduleCode) {
    return <p className="text-sm text-destructive">Unknown module route.</p>
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title={overview?.module_name ?? "ERP Module"}
        description={overview?.description}
        actions={
          canWrite ? (
            <div className="flex flex-wrap items-center gap-2">
              <Input
                className="w-48"
                placeholder="New record title…"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
              />
              <Button
                type="button"
                disabled={createMutation.isPending}
                onClick={() => createMutation.mutate()}
              >
                Add record
              </Button>
            </div>
          ) : null
        }
      />

      {linkedRoutes.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {linkedRoutes.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="inline-flex h-8 items-center rounded-md border border-input bg-background px-3 text-xs font-medium shadow-xs hover:bg-accent hover:text-accent-foreground"
            >
              <ExternalLink className="mr-1 size-3.5" aria-hidden />
              {link.label}
            </Link>
          ))}
        </div>
      ) : null}

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
          {overview?.total_records ?? 0} demo records across{" "}
          {overview?.features.length ?? 0} feature areas
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
          {overview?.features.map((f) => (
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
                <th className="px-3 py-2 font-medium">Feature</th>
                <th className="px-3 py-2 font-medium">Title</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Party</th>
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
                    <td className="px-3 py-2">
                      <Badge variant={statusVariant(r.status)}>{r.status}</Badge>
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">{r.party_name ?? "—"}</td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {r.amount != null ? Number(r.amount).toLocaleString() : "—"}
                    </td>
                    {canWrite ? (
                      <td className="px-3 py-2 text-right">
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="text-destructive"
                          disabled={deleteMutation.isPending}
                          onClick={() => deleteMutation.mutate(r.id)}
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
    </div>
  )
}
