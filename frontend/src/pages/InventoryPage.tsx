import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo, useRef, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { toast } from "sonner"

import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"
import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { LoadingOverlay, LoadingSpinner } from "@/components/ui/loading-spinner"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { InventoryFormDialog } from "@/features/inventory/InventoryFormDialog"
import { InventoryGridView } from "@/features/inventory/InventoryGridView"
import { InventoryTableView } from "@/features/inventory/InventoryTableView"
import {
  INVENTORY_PAGE_SIZE,
  buildInventoryListFilters,
} from "@/features/inventory/inventory-list-params"
import { getTablePageNumbers } from "@/features/inventory/inventory-pagination"
import {
  deleteInventoryItem,
  fetchCategories,
  fetchInventory,
  fetchInventoryItem,
} from "@/features/inventory/inventory-api"
import { useAuth } from "@/context/AuthContext"
import { canDeleteInventory } from "@/lib/permissions"
import type { InventoryItem, ItemLifecycleStatus, ItemType } from "@/types/inventory"

type ViewMode = "table" | "grid"

const SEARCH_DEBOUNCE_MS = 300

const ITEM_TYPES: ItemType[] = [
  "RAW",
  "FINISHED",
  "SEMI_FINISHED",
  "CONSUMABLE",
  "TRADING",
  "SERVICE",
  "ASSET",
]

export function InventoryPage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const itemTypeFromUrl = searchParams.get("item_type")?.toUpperCase() ?? ""
  const initialItemType = ITEM_TYPES.includes(itemTypeFromUrl as ItemType)
    ? (itemTypeFromUrl as ItemType)
    : ""
  const [viewMode, setViewMode] = useState<ViewMode>("grid")
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [categoryId, setCategoryId] = useState("")
  const [itemType, setItemType] = useState<ItemType | "">(initialItemType)
  const [lifecycleStatus, setLifecycleStatus] = useState<ItemLifecycleStatus | "">("")
  const [styleCode, setStyleCode] = useState("")
  const [colorFilter, setColorFilter] = useState("")
  const [sizeFilter, setSizeFilter] = useState("")
  const [variantsOnly, setVariantsOnly] = useState(false)
  const [tablePage, setTablePage] = useState(1)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<InventoryItem | null>(null)
  const loadMoreRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => setSearch(searchInput), SEARCH_DEBOUNCE_MS)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  useEffect(() => {
    if (ITEM_TYPES.includes(itemTypeFromUrl as ItemType)) {
      setItemType(itemTypeFromUrl as ItemType)
    }
  }, [itemTypeFromUrl])

  const filters = useMemo(
    () =>
      buildInventoryListFilters(
        search,
        categoryId,
        itemType,
        lifecycleStatus,
        styleCode,
        colorFilter,
        sizeFilter,
        variantsOnly,
      ),
    [search, categoryId, itemType, lifecycleStatus, styleCode, colorFilter, sizeFilter, variantsOnly],
  )

  useEffect(() => {
    setTablePage(1)
  }, [filters, viewMode])

  const categoriesQuery = useQuery({
    queryKey: ["inventory", "categories"],
    queryFn: fetchCategories,
  })

  const gridQuery = useInfiniteQuery({
    queryKey: ["inventory", "grid", filters],
    queryFn: ({ pageParam }) =>
      fetchInventory({
        ...filters,
        skip: pageParam,
        limit: INVENTORY_PAGE_SIZE,
        include_sales_insight: true,
      }),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce((n, p) => n + p.items.length, 0)
      if (loaded >= lastPage.total) return undefined
      return loaded
    },
    enabled: viewMode === "grid",
  })

  const tableQuery = useQuery({
    queryKey: ["inventory", "table", tablePage, filters],
    queryFn: () =>
      fetchInventory({
        ...filters,
        skip: (tablePage - 1) * INVENTORY_PAGE_SIZE,
        limit: INVENTORY_PAGE_SIZE,
        include_sales_insight: false,
      }),
    enabled: viewMode === "table",
  })

  const deleteMutation = useMutation({
    mutationFn: deleteInventoryItem,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["inventory"] })
      toast.success("Item deleted")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not delete item"
      toast.error(typeof detail === "string" ? detail : "Could not delete item")
    },
  })

  const gridItems = useMemo(
    () => gridQuery.data?.pages.flatMap((p) => p.items) ?? [],
    [gridQuery.data],
  )
  const tableItems = tableQuery.data?.items ?? []
  const items = viewMode === "grid" ? gridItems : tableItems

  const totalCount =
    viewMode === "grid"
      ? (gridQuery.data?.pages[0]?.total ?? 0)
      : (tableQuery.data?.total ?? 0)

  const tablePageCount = Math.max(1, Math.ceil(totalCount / INVENTORY_PAGE_SIZE))

  const categories = categoriesQuery.data ?? []
  const canDelete = canDeleteInventory(permissions)

  const lowStockIds = useMemo(
    () =>
      new Set(
        items
          .filter((i) => i.stock < i.low_stock_threshold)
          .map((i) => i.id),
      ),
    [items],
  )

  const activeQuery = viewMode === "grid" ? gridQuery : tableQuery
  const isInitialLoading = activeQuery.isLoading
  const isFetching =
    viewMode === "grid"
      ? gridQuery.isFetching && !gridQuery.isFetchingNextPage
      : tableQuery.isFetching

  const showCenterSpinner = isInitialLoading || isFetching
  const tablePageNumbers = getTablePageNumbers(tablePage, tablePageCount)

  const canLoadMoreGrid =
    viewMode === "grid" &&
    gridQuery.hasNextPage &&
    !gridQuery.isFetchingNextPage &&
    !showCenterSpinner

  useEffect(() => {
    if (viewMode !== "grid" || !canLoadMoreGrid) return
    const node = loadMoreRef.current
    if (!node) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting && gridQuery.hasNextPage && !gridQuery.isFetchingNextPage) {
          void gridQuery.fetchNextPage()
        }
      },
      { rootMargin: "200px" },
    )
    observer.observe(node)
    return () => observer.disconnect()
  }, [viewMode, canLoadMoreGrid, gridQuery])

  const openEdit = (item: InventoryItem) => {
    void fetchInventoryItem(item.id).then((full) => {
      setEditing(full)
      setDialogOpen(true)
    })
  }

  const confirmDelete = (item: InventoryItem) => {
    if (window.confirm(`Delete ${item.sku}?`)) {
      deleteMutation.mutate(item.id)
    }
  }

  const goToTablePage = (page: number) => {
    const next = Math.min(Math.max(1, page), tablePageCount)
    setTablePage(next)
  }

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <PageHeader
        title="Inventory"
        description="Manage item master data — SKU, classification, UOM, compliance, and status."
        actions={
          <>
            <Link to="/inventory/fabric-rolls">
              <Button type="button" variant="outline" size="sm">
                Fabric rolls
              </Button>
            </Link>
            <Link to="/inventory/variants">
              <Button type="button" variant="outline" size="sm">
                Variant matrix
              </Button>
            </Link>
            <Button
              type="button"
              data-testid="add-inventory-item"
              onClick={() => {
                setEditing(null)
                setDialogOpen(true)
              }}
            >
              Add item
            </Button>
          </>
        }
      />

      <ControlPanel className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8">
        <Input
          className="xl:col-span-2"
          placeholder="Search SKU, name, color, size…"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </Select>
        <Select value={itemType} onChange={(e) => setItemType(e.target.value as ItemType | "")}>
          <option value="">All types</option>
          <option value="RAW">Raw</option>
          <option value="FINISHED">Finished</option>
          <option value="TRADING">Trading</option>
          <option value="SERVICE">Service</option>
          <option value="ASSET">Asset</option>
        </Select>
        <Select
          value={lifecycleStatus}
          onChange={(e) => setLifecycleStatus(e.target.value as ItemLifecycleStatus | "")}
        >
          <option value="">All statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
          <option value="DISCONTINUED">Discontinued</option>
          <option value="OBSOLETE">Obsolete</option>
        </Select>
        <Input
          placeholder="Style code"
          value={styleCode}
          onChange={(e) => setStyleCode(e.target.value)}
        />
        <Input
          placeholder="Color"
          value={colorFilter}
          onChange={(e) => setColorFilter(e.target.value)}
        />
        <Input
          placeholder="Size"
          value={sizeFilter}
          onChange={(e) => setSizeFilter(e.target.value)}
        />
        <label className="flex items-center gap-2 text-sm px-1">
          <input
            type="checkbox"
            checked={variantsOnly}
            onChange={(e) => setVariantsOnly(e.target.checked)}
          />
          Variants only
        </label>
      </ControlPanel>

      <ContentSheet className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 border-b border-border pb-2">
        <Button
          type="button"
          variant={viewMode === "table" ? "default" : "outline"}
          size="sm"
          onClick={() => setViewMode("table")}
        >
          Table
        </Button>
        <Button
          type="button"
          variant={viewMode === "grid" ? "default" : "outline"}
          size="sm"
          onClick={() => setViewMode("grid")}
        >
          Grid
        </Button>
        {totalCount > 0 && !showCenterSpinner ? (
          <span className="ml-auto text-sm text-muted-foreground">
            {viewMode === "grid"
              ? `Showing ${items.length} of ${totalCount}`
              : `Page ${tablePage} of ${tablePageCount} · ${totalCount} items`}
          </span>
        ) : null}
      </div>

      {showCenterSpinner ? (
        <LoadingSpinner label="Loading inventory…" />
      ) : activeQuery.isError ? (
        <p className="text-sm text-destructive">Could not load inventory. Try again shortly.</p>
      ) : viewMode === "table" ? (
        <>
          <LoadingOverlay show={tableQuery.isFetching} label="Loading inventory…">
            <InventoryTableView
              items={tableItems}
              lowStockIds={lowStockIds}
              isAdmin={canDelete}
              deletePending={deleteMutation.isPending}
              onEdit={openEdit}
              onDelete={confirmDelete}
            />
          </LoadingOverlay>
          {totalCount > 0 && tablePageCount > 1 ? (
            <nav
              className="mt-4 flex flex-wrap items-center justify-center gap-2"
              aria-label="Inventory pagination"
            >
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={tablePage <= 1 || tableQuery.isFetching}
                onClick={() => goToTablePage(tablePage - 1)}
              >
                Previous
              </Button>
              {tablePageNumbers.map((p, idx) =>
                p === "ellipsis" ? (
                  <span key={`ellipsis-${idx}`} className="px-1 text-muted-foreground">
                    …
                  </span>
                ) : (
                  <Button
                    key={p}
                    type="button"
                    variant={p === tablePage ? "default" : "outline"}
                    size="sm"
                    disabled={tableQuery.isFetching}
                    onClick={() => goToTablePage(p)}
                  >
                    {p}
                  </Button>
                ),
              )}
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={tablePage >= tablePageCount || tableQuery.isFetching}
                onClick={() => goToTablePage(tablePage + 1)}
              >
                Next
              </Button>
            </nav>
          ) : null}
        </>
      ) : (
        <LoadingOverlay show={gridQuery.isFetchingNextPage} label="Loading more…">
          <InventoryGridView
            items={gridItems}
            lowStockIds={lowStockIds}
            isAdmin={canDelete}
            deletePending={deleteMutation.isPending}
            onEdit={openEdit}
            onDelete={confirmDelete}
          />
          <div ref={loadMoreRef} className="h-4 w-full" aria-hidden />
          {!gridQuery.hasNextPage && gridItems.length > 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">All items loaded.</p>
          ) : null}
        </LoadingOverlay>
      )}

      {viewMode === "grid" && !showCenterSpinner && gridItems.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">
          No items found. Create your first inventory item.
        </p>
      ) : null}

      {viewMode === "table" && !showCenterSpinner && tableItems.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">
          No items found. Create your first inventory item.
        </p>
      ) : null}

      </ContentSheet>

      <InventoryFormDialog
        open={dialogOpen}
        item={editing}
        onClose={() => {
          setDialogOpen(false)
          setEditing(null)
        }}
      />
    </div>
    </PosOnlyRedirect>
  )
}
