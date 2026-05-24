import { Navigate } from "react-router-dom"

import { ManagerOverviewPanel } from "@/components/ManagerOverviewPanel"
import { ManufacturingDocumentFlowChart } from "@/components/ManufacturingDocumentFlowChart"
import { PageHeader } from "@/components/PageHeader"
import { useAuth } from "@/context/AuthContext"
import { canViewManagerOverview } from "@/lib/report-access"

export function DashboardPage() {
  const { user, permissions } = useAuth()

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

  const showManagerOverview = canViewManagerOverview(permissions)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Manufacturing ERP document flow, operations KPIs, and process overview."
      />
      {showManagerOverview ? <ManagerOverviewPanel /> : null}
      <ManufacturingDocumentFlowChart />
    </div>
  )
}
