import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate, useParams } from "react-router-dom"

import { ContentSheet } from "@/components/ContentSheet"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DocumentFormDialog } from "@/features/documents/DocumentFormDialog"
import { fetchErpDocument } from "@/features/documents/documents-api"
import type { ErpDocument } from "@/types/erp-document"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"

function statusVariant(status: ErpDocument["status"]) {
  switch (status) {
    case "CONFIRMED":
      return "success" as const
    case "ISSUED":
      return "default" as const
    case "CANCELLED":
      return "danger" as const
    default:
      return "secondary" as const
  }
}

export function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>()
    const [dialogOpen, setDialogOpen] = useState(false)
  const documentId = Number(id)

  const detailQuery = useQuery({
    queryKey: ["erp-documents", "detail", documentId],
    queryFn: () => fetchErpDocument(documentId),
    enabled: Number.isFinite(documentId) && documentId > 0,
  })

  if (!Number.isFinite(documentId) || documentId <= 0) {
    return <Navigate to="/documents" replace />
  }

  if (detailQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading document…</p>
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-destructive">Document not found.</p>
        <Link
          to="/documents"
          className="text-sm text-primary hover:underline"
        >
          Back to documents
        </Link>
      </div>
    )
  }

  const doc = detailQuery.data

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link
            to="/documents"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            ← Documents
          </Link>
          <p className="mt-2 text-xs font-medium uppercase text-muted-foreground">
            Step {doc.journey_step} · {doc.phase}
          </p>
          <h1 className="mt-1 text-xl font-semibold text-foreground">{doc.title}</h1>
          <p className="text-sm text-muted-foreground">{doc.type_label}</p>
        </div>
        <Button type="button" onClick={() => setDialogOpen(true)}>
          Edit document
        </Button>
      </div>

      <ContentSheet>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <p className="text-xs uppercase text-muted-foreground">Document number</p>
          <p className="font-mono text-sm">{doc.document_number}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Status</p>
          <Badge variant={statusVariant(doc.status)} className="mt-1">
            {doc.status}
          </Badge>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Reference</p>
          <p className="text-sm">{doc.reference_number ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Created</p>
          <p className="text-sm">{new Date(doc.created_at).toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Updated</p>
          <p className="text-sm">{new Date(doc.updated_at).toLocaleString()}</p>
        </div>
        {doc.supplier_id != null ? (
          <div>
            <p className="text-xs uppercase text-muted-foreground">Supplier</p>
            <Link
              to={`/suppliers/${doc.supplier_id}`}
              className="text-sm text-primary hover:underline"
            >
              Supplier #{doc.supplier_id}
            </Link>
          </div>
        ) : null}
        {doc.customer_id != null ? (
          <div>
            <p className="text-xs uppercase text-muted-foreground">Customer</p>
            <Link
              to={`/customers/${doc.customer_id}`}
              className="text-sm text-primary hover:underline"
            >
              Customer #{doc.customer_id}
            </Link>
          </div>
        ) : null}
        {doc.purchase_id != null ? (
          <div>
            <p className="text-xs uppercase text-muted-foreground">Purchase order</p>
            <Link
              to="/purchases"
              className="text-sm text-primary hover:underline"
            >
              Purchase #{doc.purchase_id}
            </Link>
          </div>
        ) : null}
        {doc.related_document_id != null ? (
          <div>
            <p className="text-xs uppercase text-muted-foreground">Related document</p>
            <Link
              to={`/documents/${doc.related_document_id}`}
              className="text-sm text-primary hover:underline"
            >
              Document #{doc.related_document_id}
            </Link>
          </div>
        ) : null}
        {doc.notes ? (
          <div className="sm:col-span-2 lg:col-span-3">
            <p className="text-xs uppercase text-muted-foreground">Notes</p>
            <p className="whitespace-pre-wrap text-sm">{doc.notes}</p>
          </div>
        ) : null}
      </div>
      </ContentSheet>

      <ContentSheet>
      <section>
        <h2 className="text-sm font-semibold text-foreground">Content</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          {Object.keys(doc.content).length === 0
            ? "Blank template — structured fields can be added later."
            : JSON.stringify(doc.content, null, 2)}
        </p>
      </section>
      </ContentSheet>

      {doc.document_type === "BOM" ? (
        <p className="text-sm text-muted-foreground">
          Operational BOM data is managed on the{" "}
          <Link to="/bom" className="text-primary hover:underline">
            BOM
          </Link>{" "}
          page.
        </p>
      ) : null}
      {doc.document_type === "PURCHASE_ORDER" ? (
        <p className="text-sm text-muted-foreground">
          Stock purchases are managed on the{" "}
          <Link
            to="/purchases"
            className="text-primary hover:underline"
          >
            Purchases
          </Link>{" "}
          page.
        </p>
      ) : null}

      <DocumentFormDialog
        open={dialogOpen}
        document={doc}
        onClose={() => setDialogOpen(false)}
      />
    </div>
    </PosOnlyRedirect>
  )
}