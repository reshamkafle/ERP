import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  createErpDocument,
  fetchDocumentJourney,
  updateErpDocument,
} from "@/features/documents/documents-api"
import { erpDocumentFormSchema, type ErpDocumentFormValues } from "@/lib/erp-document-schema"
import type { ErpDocument, ErpDocumentType } from "@/types/erp-document"

const defaultValues: ErpDocumentFormValues = {
  document_type: "TECH_PACK",
  title: "",
  status: "DRAFT",
  reference_number: "",
  notes: "",
  supplier_id: "",
  customer_id: "",
  purchase_id: "",
  related_document_id: "",
}

function documentToForm(doc: ErpDocument): ErpDocumentFormValues {
  return {
    document_type: doc.document_type,
    title: doc.title,
    status: doc.status,
    reference_number: doc.reference_number ?? "",
    notes: doc.notes ?? "",
    supplier_id: doc.supplier_id != null ? String(doc.supplier_id) : "",
    customer_id: doc.customer_id != null ? String(doc.customer_id) : "",
    purchase_id: doc.purchase_id != null ? String(doc.purchase_id) : "",
    related_document_id:
      doc.related_document_id != null ? String(doc.related_document_id) : "",
  }
}

type Props = {
  open: boolean
  document: ErpDocument | null
  defaultType?: ErpDocumentType
  onClose: () => void
}

function Field({
  label,
  error,
  children,
}: {
  label: string
  error?: string
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {children}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  )
}

export function DocumentFormDialog({ open, document, defaultType, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = document !== null

  const journeyQuery = useQuery({
    queryKey: ["erp-documents", "journey"],
    queryFn: fetchDocumentJourney,
    enabled: open,
  })

  const form = useForm<ErpDocumentFormValues>({
    resolver: zodResolver(erpDocumentFormSchema),
    defaultValues,
  })

  useEffect(() => {
    if (!open) return
    if (document) {
      form.reset(documentToForm(document))
    } else {
      form.reset({
        ...defaultValues,
        document_type: defaultType ?? "TECH_PACK",
      })
    }
  }, [open, document, defaultType, form])

  const saveMutation = useMutation({
    mutationFn: (values: ErpDocumentFormValues) =>
      isEdit && document ? updateErpDocument(document.id, values) : createErpDocument(values),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-documents"] })
      toast.success(isEdit ? "Document updated" : "Document created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save document"
      toast.error(typeof detail === "string" ? detail : "Could not save document")
    },
  })

  if (!open) return null

  const { register, handleSubmit, formState, watch, setValue } = form
  const steps = journeyQuery.data?.steps ?? []

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-8"
      role="dialog"
      aria-modal="true"
    >
      <form
        className="w-full max-w-lg rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values) => saveMutation.mutate(values))}
      >
        <div className="border-b border-border px-4 py-3">
          <h2 className="text-lg font-semibold text-foreground">
            {isEdit ? "Edit document" : "New document"}
          </h2>
        </div>
        <div className="space-y-4 px-4 py-4">
          <Field label="Document type" error={formState.errors.document_type?.message}>
            <Select
              disabled={isEdit}
              value={watch("document_type")}
              onChange={(e) =>
                setValue("document_type", e.target.value as ErpDocumentType, {
                  shouldValidate: true,
                })
              }
            >
              {steps.map((step) => (
                <option key={step.document_type} value={step.document_type}>
                  {step.journey_step}. {step.label}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Title" error={formState.errors.title?.message}>
            <Input {...register("title")} />
          </Field>
          <Field label="Status" error={formState.errors.status?.message}>
            <Select {...register("status")}>
              <option value="DRAFT">Draft</option>
              <option value="ISSUED">Issued</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="CANCELLED">Cancelled</option>
            </Select>
          </Field>
          <Field label="Reference number" error={formState.errors.reference_number?.message}>
            <Input {...register("reference_number")} placeholder="Optional external ref" />
          </Field>
          <Field label="Notes" error={formState.errors.notes?.message}>
            <Textarea rows={3} {...register("notes")} placeholder="Document notes (blank template)" />
          </Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Supplier ID" error={formState.errors.supplier_id?.message}>
              <Input {...register("supplier_id")} placeholder="Optional" />
            </Field>
            <Field label="Customer ID" error={formState.errors.customer_id?.message}>
              <Input {...register("customer_id")} placeholder="Optional" />
            </Field>
            <Field label="Purchase ID" error={formState.errors.purchase_id?.message}>
              <Input {...register("purchase_id")} placeholder="Optional" />
            </Field>
            <Field label="Related document ID" error={formState.errors.related_document_id?.message}>
              <Input {...register("related_document_id")} placeholder="Optional chain link" />
            </Field>
          </div>
        </div>
        <div className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending} data-testid="document-create">
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  )
}
