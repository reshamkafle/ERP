import { Navigate } from "react-router-dom"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { ReportsHub } from "@/features/reports/ReportsHub"
import { useAuth } from "@/context/AuthContext"
import { canViewAnyReport } from "@/lib/report-access"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"

export function ReportsPage() {
  const { permissions } = useAuth()

  if (!canViewAnyReport(permissions)) {
    return <Navigate to="/forbidden" replace />
  }

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <PageHeader
        title="Reports"
        description="Role-scoped sales, inventory, finance, marketing, warehouse, and IT analytics."
      />
      <ContentSheet>
        <ReportsHub />
      </ContentSheet>
    </div>
    </PosOnlyRedirect>
  )
}