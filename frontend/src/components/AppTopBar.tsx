import { useLocation, useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { SpotlightSearch } from "@/components/SpotlightSearch"
import { titleForPath } from "@/lib/route-meta"
import { useAuth } from "@/context/AuthContext"

export function AppTopBar() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const title = titleForPath(pathname)

  return (
    <header
      className="flex h-[var(--topbar-height)] shrink-0 items-center gap-4 border-b border-border bg-card px-4"
      data-testid="app-topbar"
    >
      <h2 className="shrink-0 text-sm font-semibold text-foreground">{title}</h2>

      <div className="flex min-w-0 flex-1 justify-center px-2">
        <SpotlightSearch />
      </div>

      <div className="flex shrink-0 items-center gap-3 text-sm text-muted-foreground">
        <span className="hidden sm:inline">{user?.email}</span>
        <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-foreground">
          {user?.role}
        </span>
        <Button
          variant="outline"
          size="sm"
          type="button"
          data-testid="logout-button"
          onClick={() => {
            logout()
            navigate("/login", { replace: true })
          }}
        >
          Log out
        </Button>
      </div>
    </header>
  )
}
