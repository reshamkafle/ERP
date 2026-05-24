import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

/** White content sheet on gray workspace (Odoo list/form area). */
export function ContentSheet({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div className={cn("rounded-md border border-border bg-card p-4 shadow-none", className)}>
      {children}
    </div>
  )
}
