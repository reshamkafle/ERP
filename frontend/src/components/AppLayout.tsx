import { useQuery } from "@tanstack/react-query"
import { useEffect } from "react"
import { Outlet } from "react-router-dom"

import { AppSidebar } from "@/components/AppSidebar"
import { AppTopBar } from "@/components/AppTopBar"
import { api } from "@/lib/api"

export function AppLayout() {
  const { data: prefs } = useQuery({
    queryKey: ["preferences"],
    queryFn: async () => {
      const res = await api.get<{ layout: { theme?: string; sidebar_collapsed?: boolean } }>(
        "/v1/users/me/preferences",
      )
      return res.data.layout
    },
  })

  useEffect(() => {
    if (prefs?.theme === "dark") {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [prefs?.theme])

  return (
    <div
      className={`flex min-h-svh bg-workspace ${prefs?.sidebar_collapsed ? "[--sidebar-width:4rem]" : ""}`}
    >
      <AppSidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <AppTopBar />
        <main className="flex-1 overflow-y-auto p-4">
          <div className="mx-auto w-full max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
