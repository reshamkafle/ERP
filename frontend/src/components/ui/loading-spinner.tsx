import type { ReactNode } from "react"
import { Loader2 } from "lucide-react"

import { cn } from "@/lib/utils"

type LoadingSpinnerProps = {
  className?: string
  label?: string
}

/** Centered spinner for backend fetch states. */
export function LoadingSpinner({ className, label }: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className={cn("flex min-h-[280px] flex-col items-center justify-center gap-3", className)}
    >
      <Loader2 className="h-10 w-10 animate-spin text-primary" aria-hidden />
      {label ? <p className="text-sm text-muted-foreground">{label}</p> : null}
    </div>
  )
}

type LoadingOverlayProps = {
  show: boolean
  label?: string
  children: ReactNode
}

/** Wraps content and shows a centered spinner overlay while loading. */
export function LoadingOverlay({ show, label, children }: LoadingOverlayProps) {
  return (
    <div className="relative min-h-[200px]">
      {show ? (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-background/70 backdrop-blur-[1px]">
          <LoadingSpinner className="min-h-0" label={label} />
        </div>
      ) : null}
      {children}
    </div>
  )
}
