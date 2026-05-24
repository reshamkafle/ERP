import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

/** Toolbar row: search, filters, primary actions (Odoo control panel). */
export function ControlPanel({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3 rounded-md border border-border bg-card p-3 sm:flex-row sm:flex-wrap sm:items-center",
        className,
      )}
    >
      {children}
    </div>
  )
}
