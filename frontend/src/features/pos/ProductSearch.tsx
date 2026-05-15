import { useQuery } from "@tanstack/react-query"
import { Search } from "lucide-react"
import { useEffect, useRef, useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { useCartStore } from "@/features/pos/cart-store"
import { fetchPosProducts } from "@/features/pos/pos-api"
import { useDebouncedValue } from "@/features/pos/useDebouncedValue"
import { formatMoney } from "@/lib/format-money"
import type { PosProduct } from "@/types/sale"

type Props = {
  onSelectProduct?: (product: PosProduct) => void
}

export function ProductSearch({ onSelectProduct }: Props) {
  const [search, setSearch] = useState("")
  const debouncedSearch = useDebouncedValue(search, 300)
  const inputRef = useRef<HTMLInputElement>(null)
  const addProduct = useCartStore((s) => s.addProduct)

  const productsQuery = useQuery({
    queryKey: ["pos", "products", debouncedSearch],
    queryFn: () =>
      fetchPosProducts({
        search: debouncedSearch || undefined,
        limit: 24,
      }),
  })

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setSearch("")
        inputRef.current?.blur()
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  const products = productsQuery.data?.items ?? []

  function handleAdd(product: PosProduct) {
    addProduct(product, 1)
    onSelectProduct?.(product)
  }

  return (
    <section className="flex min-h-0 flex-1 flex-col gap-3">
      <SearchHeader
        inputRef={inputRef}
        search={search}
        setSearch={setSearch}
        products={products}
        onAdd={handleAdd}
      />

      <div className="min-h-0 flex-1 overflow-y-auto rounded-xl border border-border bg-card">
        {productsQuery.isLoading ? (
          <p className="p-4 text-sm text-muted-foreground">Searching…</p>
        ) : products.length === 0 ? (
          <p className="p-4 text-sm text-muted-foreground">
            {debouncedSearch ? "No products match your search." : "Type to find products."}
          </p>
        ) : (
          <ul className="divide-y divide-border">
            {products.map((product) => (
              <ProductRow key={product.id} product={product} onAdd={handleAdd} />
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}

function SearchHeader({
  inputRef,
  search,
  setSearch,
  products,
  onAdd,
}: {
  inputRef: React.RefObject<HTMLInputElement | null>
  search: string
  setSearch: (v: string) => void
  products: PosProduct[]
  onAdd: (product: PosProduct) => void
}) {
  return (
    <>
      <div className="relative">
        <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          ref={inputRef}
          className="h-11 pl-9 text-base"
          placeholder="Search name, SKU, or barcode…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && products[0]) {
              e.preventDefault()
              onAdd(products[0])
            }
          }}
          autoFocus
        />
      </div>
      <p className="text-xs text-muted-foreground">
        Enter adds the first result · Esc clears search
      </p>
    </>
  )
}

function ProductRow({
  product,
  onAdd,
}: {
  product: PosProduct
  onAdd: (product: PosProduct) => void
}) {
  const lowStock = product.stock < product.low_stock_threshold
  const outOfStock = product.stock < 1

  return (
    <li>
      <button
        type="button"
        disabled={outOfStock}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/60 disabled:cursor-not-allowed disabled:opacity-50"
        onClick={() => onAdd(product)}
      >
        <div className="min-w-0">
          <p className="truncate font-medium text-foreground">{product.name}</p>
          <p className="text-xs text-muted-foreground">
            {product.sku}
            {product.barcode ? ` · ${product.barcode}` : ""}
          </p>
          {lowStock ? (
            <Badge variant="danger" className="mt-1">
              Low: {product.stock} left
            </Badge>
          ) : (
            <span className="mt-1 inline-block text-xs text-muted-foreground">
              Stock: {product.stock}
            </span>
          )}
        </div>
        <span className="shrink-0 text-base font-semibold tabular-nums text-foreground">
          {formatMoney(product.price)}
        </span>
      </button>
    </li>
  )
}
