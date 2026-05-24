import { api } from "@/lib/api"
import type { ManagerOverview, ManagerPeriod } from "@/types/dashboard-manager"

export async function fetchManagerOverview(period: ManagerPeriod): Promise<ManagerOverview> {
  const { data } = await api.get<ManagerOverview>("/v1/dashboard/manager-overview", {
    params: { period },
  })
  return data
}
