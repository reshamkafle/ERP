import { cn } from "@/lib/utils"

type ProgressProps = {
  indeterminate?: boolean
  value?: number
  className?: string
}

/** Thin progress bar; use indeterminate while loading or saving. */
export function Progress({ indeterminate = false, value = 0, className }: ProgressProps) {
  if (indeterminate) {
    return (
      <div
        role="progressbar"
        aria-busy="true"
        aria-valuemin={0}
        aria-valuemax={100}
        className={cn("h-1 w-full overflow-hidden rounded-full bg-muted", className)}
      >
        <div className="h-full w-1/3 animate-[progress-indeterminate_1.2s_ease-in-out_infinite] rounded-full bg-primary" />
      </div>
    )
  }

  const clamped = Math.min(100, Math.max(0, value))
  return (
    <div
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
      className={cn("h-1 w-full overflow-hidden rounded-full bg-muted", className)}
    >
      <div
        className="h-full rounded-full bg-primary transition-[width] duration-200"
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
