import { Link } from "react-router-dom"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { documentStatusVariant } from "@/features/documents/document-status"
import type { ErpDocument } from "@/types/erp-document"

type DocumentGridViewProps = {
  documents: ErpDocument[]
  isAdmin: boolean
  deletePending: boolean
  onEdit: (doc: ErpDocument) => void
  onDelete: (doc: ErpDocument) => void
}

export function DocumentGridView({
  documents,
  isAdmin,
  deletePending,
  onEdit,
  onDelete,
}: DocumentGridViewProps) {
  if (documents.length === 0) {
    return null
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {documents.map((doc) => (
        <Card key={doc.id} className="flex flex-col">
          <CardHeader className="space-y-1 pb-2">
            <p className="text-xs font-medium uppercase text-muted-foreground">
              Step {doc.journey_step} · {doc.phase}
            </p>
            <CardTitle className="text-base leading-snug">
              <Link
                to={`/documents/${doc.id}`}
                className="text-primary hover:underline"
              >
                {doc.document_number}
              </Link>
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col gap-3 pt-0">
            <p className="text-sm text-foreground">{doc.title}</p>
            {doc.reference_number ? (
              <p className="text-xs text-muted-foreground">Ref: {doc.reference_number}</p>
            ) : null}
            <Badge variant={documentStatusVariant(doc.status)} className="w-fit">
              {doc.status}
            </Badge>
            <div className="mt-auto flex flex-wrap gap-2 pt-2">
              <Button type="button" variant="outline" size="sm" onClick={() => onEdit(doc)}>
                Edit
              </Button>
              {isAdmin ? (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="text-destructive"
                  disabled={deletePending}
                  onClick={() => onDelete(doc)}
                >
                  Delete
                </Button>
              ) : null}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
