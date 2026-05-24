import { Link, useLocation } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"

import { cn } from "@/lib/utils"
import { useAuth } from "@/context/AuthContext"
import { filterNavByPermissions } from "@/lib/nav-config"
import { api } from "@/lib/api"

function isActive(pathname: string, to: string): boolean {
  if (to === "/dashboard") return pathname === "/dashboard"
  return pathname === to || pathname.startsWith(`${to}/`)
}

type LayoutPrefs = {
  hidden_nav_slugs?: string[]
}

export function AppSidebar() {
  const { permissions } = useAuth()
  const { pathname } = useLocation()

  const { data: prefs } = useQuery({
    queryKey: ["preferences"],
    queryFn: async () => {
      const res = await api.get<{ layout: LayoutPrefs }>("/v1/users/me/preferences")
      return res.data.layout
    },
  })

  const groups = filterNavByPermissions(permissions, prefs?.hidden_nav_slugs ?? [])

  return (
    <aside
      className="flex w-[var(--sidebar-width)] shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground"
      data-testid="app-sidebar"
    >
      <div className="flex h-[var(--topbar-height)] items-center border-b border-sidebar-border px-4">
        <span className="text-sm font-semibold tracking-tight">ERP</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-3" aria-label="Main">
        {groups.map((group) => (
          <div key={group.title} className="mb-4 px-2">
            <p className="mb-1 px-2 text-[0.65rem] font-semibold uppercase tracking-wider text-sidebar-foreground/60">
              {group.title}
            </p>
            <ul className="space-y-0.5">
              {group.items.map((item) => {
                const Icon = item.icon
                const active = isActive(pathname, item.to)
                return (
                  <li key={item.to}>
                    <Link
                      to={item.to}
                      data-testid={`nav-${item.slug}`}
                      className={cn(
                        "flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors",
                        active
                          ? "bg-sidebar-accent font-medium text-sidebar-accent-foreground"
                          : "text-sidebar-foreground/90 hover:bg-sidebar-accent/80 hover:text-sidebar-accent-foreground",
                      )}
                    >
                      <Icon className="size-4 shrink-0 opacity-90" aria-hidden />
                      {item.label}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  )
}
