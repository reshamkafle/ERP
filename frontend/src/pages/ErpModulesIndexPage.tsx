import { useQuery } from "@tanstack/react-query"

import { AppLauncherGrid } from "@/components/AppLauncherGrid"
import { PageHeader } from "@/components/PageHeader"
import { useAuth } from "@/context/AuthContext"
import { api } from "@/lib/api"
import { DASHBOARD_APPS } from "@/lib/erp-apps"
import type { DashboardSummary } from "@/types/user"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"
import { canAccess } from "@/lib/permissions"

export function ErpModulesIndexPage() {
  const { permissions } = useAuth()

  const summaryQuery = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: async () => {
      const { data } = await api.get<DashboardSummary>("/v1/dashboard/summary")
      return data
    },
    enabled: canAccess(permissions, "reports.dashboard.read"),
  })

  const lowStock = summaryQuery.data?.low_stock_count
  const openPos = summaryQuery.data?.open_pos_sessions

  return (
    <PosOnlyRedirect>
    <div className="space-y-6">
      <PageHeader
        title="ERP Modules"
        description="Choose an app to get started."
      />

      <div className="flex min-h-[min(28rem,calc(100svh-12rem))] flex-col items-center justify-center px-2 py-8">
        <AppLauncherGrid apps={DASHBOARD_APPS} />
      </div>

      {!summaryQuery.isLoading && (lowStock != null || openPos != null) ? (
        <div className="mx-auto flex max-w-2xl flex-wrap justify-center gap-4 text-center text-sm text-muted-foreground">
          {lowStock != null ? (
            <span>
              <span className="font-semibold text-primary">{lowStock}</span> low stock SKU
              {lowStock === 1 ? "" : "s"}
            </span>
          ) : null}
          {lowStock != null && openPos != null ? <span aria-hidden>·</span> : null}
          {openPos != null ? (
            <span>
              <span className="font-semibold text-primary">{openPos}</span> open POS session
              {openPos === 1 ? "" : "s"}
            </span>
          ) : null}
        </div>
      ) : null}

      {summaryQuery.isError ? (
        <p className="text-center text-sm text-destructive">
          Could not load dashboard summary. Apps are still available above.
        </p>
      ) : null}
    </div>
    </PosOnlyRedirect>
  )
}