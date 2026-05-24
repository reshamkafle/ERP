import { Link } from "react-router-dom"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { documentStatusVariant } from "@/features/documents/document-status"
import type { ErpDocument } from "@/types/erp-document"

type DocumentTableViewProps = {
  documents: ErpDocument[]
  isAdmin: boolean
  deletePending: boolean
  onEdit: (doc: ErpDocument) => void
  onDelete: (doc: ErpDocument) => void
}

export function DocumentTableView({
  documents,
  isAdmin,
  deletePending,
  onEdit,
  onDelete,
}: DocumentTableViewProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
          <tr>
            <th className="px-3 py-2 font-medium">Number</th>
            <th className="px-3 py-2 font-medium">Title</th>
            <th className="px-3 py-2 font-medium">Reference</th>
            <th className="px-3 py-2 font-medium">Status</th>
            <th className="px-3 py-2 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.length === 0 ? null : (
            documents.map((doc) => (
              <tr key={doc.id} className="border-b border-border last:border-0">
                <td className="px-3 py-2 font-mono text-xs">
                  <Link
                    to={`/documents/${doc.id}`}
                    className="font-medium text-primary hover:underline"
                  >
                    {doc.document_number}
                  </Link>
                </td>
                <td className="px-3 py-2">{doc.title}</td>
                <td className="px-3 py-2 text-muted-foreground">
                  {doc.reference_number ?? "—"}
                </td>
                <td className="px-3 py-2">
                  <Badge variant={documentStatusVariant(doc.status)}>{doc.status}</Badge>
                </td>
                <td className="px-3 py-2 text-right">
                  <Button type="button" variant="ghost" size="sm" onClick={() => onEdit(doc)}>
                    Edit
                  </Button>
                  {isAdmin ? (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="text-destructive"
                      disabled={deletePending}
                      onClick={() => onDelete(doc)}
                    >
                      Delete
                    </Button>
                  ) : null}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
