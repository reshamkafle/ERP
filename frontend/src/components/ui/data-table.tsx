import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

export function DataTable({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("overflow-x-auto rounded-md border border-border bg-card", className)}>
      <table className="w-full min-w-[640px] border-collapse text-sm">{children}</table>
    </div>
  )
}

export function DataTableHead({ children }: { children: ReactNode }) {
  return (
    <thead className="border-b border-border bg-muted/50 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
      {children}
    </thead>
  )
}

export function DataTableBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-border">{children}</tbody>
}

export function DataTableRow({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <tr className={cn("transition-colors hover:bg-muted/40", className)}>{children}</tr>
  )
}

export function DataTableCell({
  children,
  className,
  header,
}: {
  children: ReactNode
  className?: string
  header?: boolean
}) {
  const Tag = header ? "th" : "td"
  return (
    <Tag
      className={cn(
        "px-3 py-2.5 align-middle",
        header ? "font-semibold" : "text-foreground",
        className,
      )}
    >
      {children}
    </Tag>
  )
}
