import { Link } from "react-router-dom"

import { cn } from "@/lib/utils"
import type { ErpApp } from "@/lib/erp-apps"

type AppLauncherGridProps = {
  apps: ErpApp[]
  className?: string
}

/** Odoo home-menu style app tiles (colored icon + label). */
export function AppLauncherGrid({ apps, className }: AppLauncherGridProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-3 gap-x-6 gap-y-8 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6",
        className,
      )}
      data-testid="app-launcher"
    >
      {apps.map((app) => {
        const Icon = app.icon
        return (
          <Link
            key={app.to}
            to={app.to}
            data-testid={`app-${app.slug}`}
            className="group flex flex-col items-center gap-2 rounded-lg p-2 outline-none transition-colors hover:bg-muted/60 focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            <span
              className={cn(
                "flex size-[4.5rem] items-center justify-center rounded-xl shadow-sm transition-transform group-hover:scale-105",
                app.tileClass,
              )}
            >
              <Icon className={cn("size-8", app.iconClass)} strokeWidth={1.75} aria-hidden />
            </span>
            <span className="max-w-[6.5rem] text-center text-xs font-medium leading-tight text-foreground">
              {app.label}
            </span>
          </Link>
        )
      })}
    </div>
  )
}
