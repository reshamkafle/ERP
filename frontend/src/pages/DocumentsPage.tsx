import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo, useRef, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { LoadingOverlay, LoadingSpinner } from "@/components/ui/loading-spinner"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { DocumentFormDialog } from "@/features/documents/DocumentFormDialog"
import { DocumentGridView } from "@/features/documents/DocumentGridView"
import { DocumentTableView } from "@/features/documents/DocumentTableView"
import {
  DOCUMENTS_PAGE_SIZE,
  buildDocumentsListFilters,
} from "@/features/documents/documents-list-params"
import {
  deleteErpDocument,
  fetchDocumentJourney,
  fetchErpDocuments,
} from "@/features/documents/documents-api"
import { getTablePageNumbers } from "@/features/inventory/inventory-pagination"
import { useAuth } from "@/context/AuthContext"
import type { ErpDocument, ErpDocumentType, JourneyStep } from "@/types/erp-document"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"
import { canDeleteDocuments } from "@/lib/permissions"

type ViewMode = "table" | "grid"

const SEARCH_DEBOUNCE_MS = 300

const DOCUMENT_TYPES: ErpDocumentType[] = [
  "TECH_PACK",
  "BOM",
  "PURCHASE_ORDER",
  "GRN",
  "INSPECTION_REPORT",
  "LAB_TEST_REPORT",
  "PRODUCTION_ORDER",
  "STOCK_TRANSFER",
  "INVENTORY_ADJUSTMENT",
  "PICK_LIST",
  "PACKING_LIST",
  "SHIPPING_MARKS",
  "ASN",
  "COMMERCIAL_INVOICE",
  "OUTGOING_INVOICE",
  "BILL_OF_LADING",
  "CERTIFICATE_OF_ORIGIN",
  "EXPORT_DECLARATION",
  "LETTER_OF_CREDIT",
  "BILL_OF_EXCHANGE",
  "PROOF_OF_DELIVERY",
  "PAYMENT_RECORD",
  "LANDED_COST",
]

export function DocumentsPage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const typeFromUrl = searchParams.get("type")?.toUpperCase() ?? ""
  const initialType = DOCUMENT_TYPES.includes(typeFromUrl as ErpDocumentType)
    ? (typeFromUrl as ErpDocumentType)
    : "TECH_PACK"
  const [viewMode, setViewMode] = useState<ViewMode>("grid")
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [activeType, setActiveType] = useState<ErpDocumentType>(initialType)
  const [tablePage, setTablePage] = useState(1)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<ErpDocument | null>(null)
  const [defaultType, setDefaultType] = useState<ErpDocumentType | undefined>()
  const loadMoreRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => setSearch(searchInput), SEARCH_DEBOUNCE_MS)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  useEffect(() => {
    if (DOCUMENT_TYPES.includes(typeFromUrl as ErpDocumentType)) {
      setActiveType(typeFromUrl as ErpDocumentType)
    }
  }, [typeFromUrl])

  const journeyQuery = useQuery({
    queryKey: ["erp-documents", "journey"],
    queryFn: fetchDocumentJourney,
  })

  const filters = useMemo(
    () => buildDocumentsListFilters(search, activeType),
    [search, activeType],
  )

  useEffect(() => {
    setTablePage(1)
  }, [filters, viewMode])

  const activeStep: JourneyStep | undefined = journeyQuery.data?.steps.find(
    (s) => s.document_type === activeType,
  )

  const gridQuery = useInfiniteQuery({
    queryKey: ["erp-documents", "grid", filters],
    queryFn: ({ pageParam }) =>
      fetchErpDocuments({
        ...filters,
        skip: pageParam,
        limit: DOCUMENTS_PAGE_SIZE,
      }),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce((n, p) => n + p.items.length, 0)
      if (loaded >= lastPage.total) return undefined
      return loaded
    },
    enabled: viewMode === "grid" && journeyQuery.isSuccess,
  })

  const tableQuery = useQuery({
    queryKey: ["erp-documents", "table", tablePage, filters],
    queryFn: () =>
      fetchErpDocuments({
        ...filters,
        skip: (tablePage - 1) * DOCUMENTS_PAGE_SIZE,
        limit: DOCUMENTS_PAGE_SIZE,
      }),
    enabled: viewMode === "table" && journeyQuery.isSuccess,
  })

  const deleteMutation = useMutation({
    mutationFn: deleteErpDocument,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-documents"] })
      toast.success("Document deleted")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not delete document"
      toast.error(typeof detail === "string" ? detail : "Could not delete document")
    },
  })

  const gridDocuments = useMemo(
    () => gridQuery.data?.pages.flatMap((p) => p.items) ?? [],
    [gridQuery.data],
  )
  const tableDocuments = tableQuery.data?.items ?? []
  const documents = viewMode === "grid" ? gridDocuments : tableDocuments

  const totalCount =
    viewMode === "grid"
      ? (gridQuery.data?.pages[0]?.total ?? 0)
      : (tableQuery.data?.total ?? 0)

  const tablePageCount = Math.max(1, Math.ceil(totalCount / DOCUMENTS_PAGE_SIZE))
  const canDelete = canDeleteDocuments(permissions)

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

  const openEdit = (doc: ErpDocument) => {
    setEditing(doc)
    setDefaultType(undefined)
    setDialogOpen(true)
  }

  const confirmDelete = (doc: ErpDocument) => {
    if (window.confirm(`Delete ${doc.document_number}?`)) {
      deleteMutation.mutate(doc.id)
    }
  }

  const goToTablePage = (page: number) => {
    const next = Math.min(Math.max(1, page), tablePageCount)
    setTablePage(next)
  }

  const openNew = () => {
    setEditing(null)
    setDefaultType(activeType)
    setDialogOpen(true)
  }

  const steps = journeyQuery.data?.steps ?? []

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <PageHeader
        title="Documents"
        description="ERP document journey — product definition through export, delivery, and costing."
        actions={
          <Button type="button" onClick={openNew} disabled={!activeStep} data-testid="new-document">
            {activeStep ? `Add ${activeStep.number_prefix}` : "New document"}
          </Button>
        }
      />

      {journeyQuery.isLoading ? (
        <LoadingSpinner label="Loading document types…" />
      ) : journeyQuery.isError ? (
        <p className="text-sm text-destructive">Could not load document journey.</p>
      ) : (
        <>
          <div className="-mx-1 overflow-x-auto px-1 pb-1">
            <div className="flex min-w-max gap-2 border-b border-border pb-2">
              {steps.map((step) => (
                <Button
                  key={step.document_type}
                  type="button"
                  variant={activeType === step.document_type ? "default" : "outline"}
                  size="sm"
                  className="shrink-0"
                  onClick={() => setActiveType(step.document_type)}
                  title={step.label}
                >
                  {step.number_prefix}
                </Button>
              ))}
            </div>
          </div>

          {activeStep ? (
            <ContentSheet className="space-y-4">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-xs font-medium uppercase text-muted-foreground">
                    Step {activeStep.journey_step} · {activeStep.phase}
                  </p>
                  <h2 className="text-lg font-semibold text-foreground">{activeStep.label}</h2>
                </div>
                {totalCount > 0 && !showCenterSpinner ? (
                  <Badge variant="secondary" className="w-fit">
                    {totalCount} record{totalCount === 1 ? "" : "s"}
                  </Badge>
                ) : null}
              </div>

              <ControlPanel>
                <Input
                  className="max-w-lg"
                  placeholder="Search by title, number, or reference…"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                />
              </ControlPanel>

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
                      ? `Showing ${documents.length} of ${totalCount}`
                      : `Page ${tablePage} of ${tablePageCount} · ${totalCount} documents`}
                  </span>
                ) : null}
              </div>

              {showCenterSpinner ? (
                <LoadingSpinner label="Loading documents…" />
              ) : activeQuery.isError ? (
                <p className="text-sm text-destructive">Could not load documents. Try again shortly.</p>
              ) : viewMode === "table" ? (
                <>
                  <LoadingOverlay show={tableQuery.isFetching} label="Loading documents…">
                    <DocumentTableView
                      documents={tableDocuments}
                      isAdmin={canDelete}
                      deletePending={deleteMutation.isPending}
                      onEdit={openEdit}
                      onDelete={confirmDelete}
                    />
                  </LoadingOverlay>
                  {totalCount > 0 && tablePageCount > 1 ? (
                    <nav
                      className="mt-4 flex flex-wrap items-center justify-center gap-2"
                      aria-label="Documents pagination"
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
                  <DocumentGridView
                    documents={gridDocuments}
                    isAdmin={canDelete}
                    deletePending={deleteMutation.isPending}
                    onEdit={openEdit}
                    onDelete={confirmDelete}
                  />
                  <div ref={loadMoreRef} className="h-4 w-full" aria-hidden />
                  {!gridQuery.hasNextPage && gridDocuments.length > 0 ? (
                    <p className="py-4 text-center text-sm text-muted-foreground">
                      All documents loaded.
                    </p>
                  ) : null}
                </LoadingOverlay>
              )}

              {viewMode === "grid" && !showCenterSpinner && gridDocuments.length === 0 ? (
                <p className="py-12 text-center text-sm text-muted-foreground">
                  No documents yet. Add the first {activeStep.number_prefix} record.
                </p>
              ) : null}

              {viewMode === "table" && !showCenterSpinner && tableDocuments.length === 0 ? (
                <p className="py-12 text-center text-sm text-muted-foreground">
                  No documents yet. Add the first {activeStep.number_prefix} record.
                </p>
              ) : null}
            </ContentSheet>
          ) : null}
        </>
      )}

      <DocumentFormDialog
        open={dialogOpen}
        document={editing}
        defaultType={defaultType}
        onClose={() => setDialogOpen(false)}
      />
    </div>
    </PosOnlyRedirect>
  )
}