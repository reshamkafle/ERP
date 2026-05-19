import { Link, Outlet, useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const canSeeDashboard = user?.role === "ADMIN" || user?.role === "MANAGER"

  return (
    <div className="flex min-h-svh flex-col bg-background">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
          <div className="flex items-center gap-6">
            <span className="text-sm font-semibold text-foreground">ERP</span>
            <nav className="flex items-center gap-3 text-sm">
              {canSeeDashboard ? (
                <>
                  <Link className="text-muted-foreground hover:text-foreground" to="/dashboard">
                    Dashboard
                  </Link>
                  <Link className="text-muted-foreground hover:text-foreground" to="/reports">
                    Reports
                  </Link>
                  <Link className="text-muted-foreground hover:text-foreground" to="/inventory">
                    Inventory
                  </Link>
                  <Link className="text-muted-foreground hover:text-foreground" to="/customers">
                    Customers
                  </Link>
                  <Link className="text-muted-foreground hover:text-foreground" to="/suppliers">
                    Suppliers
                  </Link>
                  <Link className="text-muted-foreground hover:text-foreground" to="/purchases">
                    Purchases
                  </Link>
                  <Link className="text-muted-foreground hover:text-foreground" to="/promotions">
                    Promotions
                  </Link>
                </>
              ) : null}
              <Link className="text-muted-foreground hover:text-foreground" to="/sales">
                Sales
              </Link>
              <Link className="text-muted-foreground hover:text-foreground" to="/pos">
                POS
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <span className="hidden sm:inline">{user?.email}</span>
            <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-foreground">
              {user?.role}
            </span>
            <Button
              variant="outline"
              size="sm"
              type="button"
              onClick={() => {
                logout()
                navigate("/login", { replace: true })
              }}
            >
              Log out
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
