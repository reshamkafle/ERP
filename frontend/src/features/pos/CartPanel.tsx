import { Minus, Trash2 } from "lucide-react"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { CustomerLookup } from "@/features/pos/CustomerLookup"
import { cartSubtotal, useCartStore, type CartLine } from "@/features/pos/cart-store"
import { formatMoney } from "@/lib/format-money"

type Props = {
  onCheckout: () => void
  isCheckingOut: boolean
}

export function CartPanel({ onCheckout, isCheckingOut }: Props) {
  const lines = useCartStore((s) => s.lines)
  const removeLine = useCartStore((s) => s.removeLine)
  const setQuantity = useCartStore((s) => s.setQuantity)
  const adjustQuantity = useCartStore((s) => s.adjustQuantity)
  const clearCart = useCartStore((s) => s.clearCart)

  const subtotal = cartSubtotal(lines)
  const total = subtotal

  return (
    <section className="flex h-full min-h-[28rem] flex-col rounded-xl border border-border bg-card shadow-sm">
      <header className="flex items-center justify-between border-b border-border px-4 py-3">
        <h2 className="text-lg font-semibold text-foreground">Cart</h2>
        {lines.length > 0 ? (
          <Button type="button" variant="ghost" size="sm" onClick={clearCart}>
            Clear
          </Button>
        ) : null}
      </header>

      <CartScrollArea
        lines={lines}
        removeLine={removeLine}
        setQuantity={setQuantity}
        adjustQuantity={adjustQuantity}
      />

      <footer className="space-y-3 border-t border-border p-4">
        <CustomerLookup />
        <CartTotals subtotal={subtotal} total={total} />
        <Button
          type="button"
          size="lg"
          className="h-12 w-full text-base"
          disabled={lines.length === 0 || isCheckingOut}
          onClick={onCheckout}
        >
          {isCheckingOut ? "Processing…" : `Checkout · ${formatMoney(total)}`}
        </Button>
      </footer>
    </section>
  )
}

function CartScrollArea({
  lines,
  removeLine,
  setQuantity,
  adjustQuantity,
}: {
  lines: CartLine[]
  removeLine: (id: number) => void
  setQuantity: (id: number, qty: number) => void
  adjustQuantity: (id: number, delta: number) => void
}) {
  return (
    <div className="min-h-0 flex-1 overflow-y-auto p-2">
      {lines.length === 0 ? (
        <p className="px-2 py-6 text-center text-sm text-muted-foreground">
          Search and tap products to add them here.
        </p>
      ) : (
        <ul className="space-y-2">
          {lines.map((line) => (
            <CartLineRow
              key={line.productId}
              line={line}
              onRemove={() => removeLine(line.productId)}
              onAdjust={(delta) => adjustQuantity(line.productId, delta)}
              onSetQuantity={(qty) => setQuantity(line.productId, qty)}
            />
          ))}
        </ul>
      )}
    </div>
  )
}

function CartTotals({ subtotal, total }: { subtotal: number; total: number }) {
  return (
    <div className="space-y-1 text-sm">
      <div className="flex justify-between text-muted-foreground">
        <span>Subtotal</span>
        <span className="tabular-nums">{formatMoney(subtotal)}</span>
      </div>
      <div className="flex justify-between text-muted-foreground">
        <span>Tax (0%)</span>
        <span className="tabular-nums">{formatMoney(0)}</span>
      </div>
      <TotalRow total={total} />
    </div>
  )
}

function TotalRow({ total }: { total: number }) {
  return (
    <div className="flex justify-between text-base font-semibold text-foreground">
      <span>Total</span>
      <span className="tabular-nums text-primary">
        {formatMoney(total)}
      </span>
    </div>
  )
}

function CartLineRow({
  line,
  onRemove,
  onAdjust,
  onSetQuantity,
}: {
  line: CartLine
  onRemove: () => void
  onAdjust: (delta: number) => void
  onSetQuantity: (qty: number) => void
}) {
  const [customQty, setCustomQty] = useState(String(line.quantity))
  const lineTotal = line.price * line.quantity

  useEffect(() => {
    setCustomQty(String(line.quantity))
  }, [line.quantity])

  return (
    <li className="rounded-lg border border-border bg-background/80 p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate font-medium text-foreground">{line.name}</p>
          <p className="text-xs text-muted-foreground">
            {line.sku} · {formatMoney(line.price)} each
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className="text-sm font-semibold tabular-nums">{formatMoney(lineTotal)}</span>
          <Button type="button" variant="ghost" size="icon-sm" onClick={onRemove} aria-label="Remove">
            <Trash2 className="size-4" />
          </Button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <Button type="button" variant="outline" size="sm" onClick={() => onAdjust(-1)} aria-label="Decrease">
          <Minus className="size-3.5" />
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={() => onAdjust(1)}>
          +1
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={() => onAdjust(5)}>
          +5
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={() => onAdjust(10)}>
          +10
        </Button>
        <Input
          className="h-8 w-16 text-center tabular-nums"
          inputMode="numeric"
          value={customQty}
          onChange={(e) => setCustomQty(e.target.value)}
          onBlur={() => {
            const parsed = Number.parseInt(customQty, 10)
            if (Number.isFinite(parsed)) onSetQuantity(parsed)
            else setCustomQty(String(line.quantity))
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") e.currentTarget.blur()
          }}
          aria-label="Quantity"
        />
      </div>
    </li>
  )
}
