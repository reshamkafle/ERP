import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { toast } from "sonner"

import { CartPanel } from "@/features/pos/CartPanel"
import { checkoutSale } from "@/features/pos/pos-api"
import { ProductSearch } from "@/features/pos/ProductSearch"
import { ReceiptDialog } from "@/features/pos/ReceiptDialog"
import { useCartStore } from "@/features/pos/cart-store"
import type { Sale } from "@/types/sale"

export function PosShell() {
  const queryClient = useQueryClient()
  const lines = useCartStore((s) => s.lines)
  const selectedCustomer = useCartStore((s) => s.selectedCustomer)
  const clearCart = useCartStore((s) => s.clearCart)
  const [lastSale, setLastSale] = useState<Sale | null>(null)

  const checkoutMutation = useMutation({
    mutationFn: checkoutSale,
    onSuccess: (sale) => {
      clearCart()
      setLastSale(sale)
      void queryClient.invalidateQueries({ queryKey: ["pos", "products"] })
      void queryClient.invalidateQueries({ queryKey: ["inventory"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      void queryClient.invalidateQueries({ queryKey: ["customers"] })
      void queryClient.invalidateQueries({ queryKey: ["sales"] })
      toast.success(`Sale #${sale.id} completed`)
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Checkout failed"
      toast.error(typeof detail === "string" ? detail : "Checkout failed")
    },
  })

  function handleCheckout() {
    if (lines.length === 0) return
    checkoutMutation.mutate({
      customer_id: selectedCustomer?.id ?? null,
      items: lines.map((line) => ({
        product_id: line.productId,
        quantity: line.quantity,
      })),
    })
  }

  return (
    <PosLayout>
      <header className="mb-4">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Point of sale</h1>
        <p className="text-sm text-muted-foreground">Search products, build a cart, and checkout.</p>
      </header>

      <div className="grid min-h-[32rem] gap-4 lg:grid-cols-[1fr_22rem] xl:grid-cols-[1fr_24rem]">
        <ProductSearch />
        <CartPanel onCheckout={handleCheckout} isCheckingOut={checkoutMutation.isPending} />
      </div>

      <ReceiptDialog sale={lastSale} onClose={() => setLastSale(null)} />
    </PosLayout>
  )
}

function PosLayout({ children }: { children: React.ReactNode }) {
  return <div className="mx-auto w-full max-w-7xl">{children}</div>
}
