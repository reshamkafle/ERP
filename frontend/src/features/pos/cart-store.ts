import { create } from "zustand"

import type { PosProduct } from "@/types/sale"

export type CartLine = {
  productId: number
  sku: string
  name: string
  price: number
  stock: number
  quantity: number
}

export type SelectedCustomer = {
  id: number
  name: string
  phone: string | null
}

type CartState = {
  lines: CartLine[]
  selectedCustomer: SelectedCustomer | null
  addProduct: (product: PosProduct, quantity?: number) => void
  removeLine: (productId: number) => void
  setQuantity: (productId: number, quantity: number) => void
  adjustQuantity: (productId: number, delta: number) => void
  setSelectedCustomer: (customer: SelectedCustomer | null) => void
  clearCart: () => void
}

function parsePrice(price: string): number {
  const n = Number.parseFloat(price)
  return Number.isFinite(n) ? n : 0
}

export const useCartStore = create<CartState>((set) => ({
  lines: [],
  selectedCustomer: null,

  addProduct: (product, quantity = 1) => {
    const qty = Math.max(1, quantity)
    set((state) => {
      const existing = state.lines.find((l) => l.productId === product.id)
      if (existing) {
        const nextQty = Math.min(existing.quantity + qty, product.stock)
        if (nextQty < 1) return state
        return {
          lines: state.lines.map((l) =>
            l.productId === product.id ? { ...l, quantity: nextQty, stock: product.stock } : l,
          ),
        }
      }
      if (product.stock < 1) return state
      return {
        lines: [
          ...state.lines,
          {
            productId: product.id,
            sku: product.sku,
            name: product.name,
            price: parsePrice(product.price),
            stock: product.stock,
            quantity: Math.min(qty, product.stock),
          },
        ],
      }
    })
  },

  removeLine: (productId) =>
    set((state) => ({ lines: state.lines.filter((l) => l.productId !== productId) })),

  setQuantity: (productId, quantity) =>
    set((state) => ({
      lines: state.lines.map((l) => {
        if (l.productId !== productId) return l
        const next = Math.max(1, Math.min(quantity, l.stock))
        return { ...l, quantity: next }
      }),
    })),

  adjustQuantity: (productId, delta) =>
    set((state) => ({
      lines: state.lines
        .map((l) => {
          if (l.productId !== productId) return l
          const next = Math.max(1, Math.min(l.quantity + delta, l.stock))
          return { ...l, quantity: next }
        })
        .filter((l) => l.quantity > 0),
    })),

  setSelectedCustomer: (customer) => set({ selectedCustomer: customer }),

  clearCart: () => set({ lines: [], selectedCustomer: null }),
}))

export function cartSubtotal(lines: CartLine[]): number {
  return lines.reduce((sum, l) => sum + l.price * l.quantity, 0)
}
