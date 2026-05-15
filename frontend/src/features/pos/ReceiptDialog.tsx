import { Button } from "@/components/ui/button"
import { formatMoney } from "@/lib/format-money"
import type { Sale } from "@/types/sale"

type Props = {
  sale: Sale | null
  onClose: () => void
}

export function ReceiptDialog({ sale, onClose }: Props) {
  if (!sale) return null

  const created = new Date(sale.created_at).toLocaleString()

  return (
    <DialogBackdrop onClose={onClose}>
      <DialogCard>
        <header className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-lg font-semibold">Sale #{sale.id}</h2>
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        </header>

        <DialogBody sale={sale} created={created} />

        <footer className="border-t border-border p-4">
          <Button type="button" className="w-full" onClick={onClose}>
            Done
          </Button>
        </footer>
      </DialogCard>
    </DialogBackdrop>
  )
}

function DialogBackdrop({
  children,
  onClose,
}: {
  children: React.ReactNode
  onClose: () => void
}) {
  return (
    <BackdropShell onClick={onClose}>
      <BackdropInner>{children}</BackdropInner>
    </BackdropShell>
  )
}

function BackdropInner({ children }: { children: React.ReactNode }) {
  return <div onClick={(e) => e.stopPropagation()}>{children}</div>
}

function BackdropShell({
  children,
  onClick,
}: {
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="dialog"
      aria-modal="true"
      onClick={onClick}
    >
      {children}
    </div>
  )
}

function DialogCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-full max-w-md rounded-xl border border-border bg-card shadow-lg">
      {children}
    </div>
  )
}

function DialogBody({ sale, created }: { sale: Sale; created: string }) {
  return (
    <div className="max-h-[60vh] space-y-4 overflow-y-auto p-4 text-sm">
      <p className="text-muted-foreground">{created}</p>

      <ul className="divide-y divide-border rounded-lg border border-border">
        {sale.items.map((item) => (
          <li key={item.id} className="flex justify-between gap-3 px-3 py-2">
            <div className="min-w-0">
              <p className="font-medium text-foreground">{item.product_name}</p>
              <p className="text-xs text-muted-foreground">
                {item.quantity} × {formatMoney(item.price_at_sale)}
              </p>
            </div>
            <span className="shrink-0 font-medium tabular-nums">
              {formatMoney(item.line_total)}
            </span>
          </li>
        ))}
      </ul>

      <div className="space-y-1 border-t border-border pt-3">
        <ReceiptRow label="Subtotal" value={formatMoney(sale.subtotal)} muted />
        <ReceiptRow label="Tax" value={formatMoney(sale.tax)} muted />
        <ReceiptRow label="Total paid" value={formatMoney(sale.total)} emphasis />
      </div>
    </div>
  )
}

function ReceiptRow({
  label,
  value,
  muted,
  emphasis,
}: {
  label: string
  value: string
  muted?: boolean
  emphasis?: boolean
}) {
  if (emphasis) {
    return (
      <div className="flex justify-between text-base font-semibold text-foreground">
        <span>{label}</span>
        <span className="tabular-nums text-emerald-600 dark:text-emerald-400">{value}</span>
      </div>
    )
  }
  return (
    <div className={`flex justify-between ${muted ? "text-muted-foreground" : ""}`}>
      <span>{label}</span>
      <span className="tabular-nums">{value}</span>
    </div>
  )
}
