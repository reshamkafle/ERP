import { useQuery } from "@tanstack/react-query"
import { Navigate } from "react-router-dom"

import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import type { DashboardSummary } from "@/types/user"

export function DashboardPage() {
  const { user } = useAuth()

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

  const summaryQuery = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: async () => {
      const { data } = await api.get<DashboardSummary>("/v1/dashboard/summary")
      return data
    },
    enabled: user?.role === "ADMIN" || user?.role === "MANAGER",
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Key metrics for managers and administrators.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Snapshot
          </p>
          <p className="mt-2 text-lg font-semibold text-foreground">
            {summaryQuery.isLoading ? "Loading…" : summaryQuery.data?.heading ?? "—"}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Low stock SKUs
          </p>
          <p className="mt-2 text-3xl font-semibold text-foreground">
            {summaryQuery.isLoading ? "…" : summaryQuery.data?.low_stock_count ?? "—"}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Open POS sessions
          </p>
          <p className="mt-2 text-3xl font-semibold text-foreground">
            {summaryQuery.isLoading ? "…" : summaryQuery.data?.open_pos_sessions ?? "—"}
          </p>
        </div>
      </div>
      {summaryQuery.isError ? (
        <p className="text-sm text-destructive">Could not load dashboard data. Try again shortly.</p>
      ) : null}
    </div>
  )
}
