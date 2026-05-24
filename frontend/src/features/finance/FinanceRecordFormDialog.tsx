import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo } from "react"
import { useFieldArray, useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  createModuleRecord,
  fetchModuleRecord,
  updateModuleRecord,
} from "@/features/modules/modules-api"
import {
  FINANCE_FEATURE_OPTIONS,
  getFinanceSectionsForFeature,
  lineItemFields,
  type FinanceFieldDef,
} from "@/lib/finance-field-groups"
import {
  defaultFinanceFormValues,
  emptyLineItem,
  FINANCE_MODULE_CODE,
  financeFormSchema,
  formToCreatePayload,
  formToUpdatePayload,
  newFinanceReference,
  recordToForm,
  type FinanceFormValues,
} from "@/lib/finance-record-schema"

type Props = {
  open: boolean
  editingId: number | null
  defaultFeatureCode: string
  onClose: () => void
}

export function FinanceRecordFormDialog({
  open,
  editingId,
  defaultFeatureCode,
  onClose,
}: Props) {
  const queryClient = useQueryClient()
  const isEdit = editingId !== null

  const recordQuery = useQuery({
    queryKey: ["erp-modules", FINANCE_MODULE_CODE, "record", editingId],
    queryFn: () => fetchModuleRecord(FINANCE_MODULE_CODE, editingId!),
    enabled: open && isEdit,
  })

  const form = useForm<FinanceFormValues>({
    resolver: zodResolver(financeFormSchema),
    defaultValues: defaultFinanceFormValues,
  })

  const featureCode = form.watch("feature_code")
  const sections = useMemo(() => getFinanceSectionsForFeature(featureCode), [featureCode])

  const lineItemsArray = useFieldArray({
    control: form.control,
    name: "transactional.line_items",
  })

  useEffect(() => {
    if (!open) return
    if (isEdit && recordQuery.data) {
      form.reset(recordToForm(recordQuery.data))
      return
    }
    if (!isEdit) {
      form.reset({
        ...defaultFinanceFormValues,
        feature_code: defaultFeatureCode || "general_ledger",
        reference: newFinanceReference(),
      })
    }
  }, [open, isEdit, recordQuery.data, defaultFeatureCode, form])

  const saveMutation = useMutation({
    mutationFn: async (values: FinanceFormValues) => {
      if (isEdit && editingId) {
        return updateModuleRecord(
          FINANCE_MODULE_CODE,
          editingId,
          formToUpdatePayload(values),
        )
      }
      return createModuleRecord(FINANCE_MODULE_CODE, formToCreatePayload(values))
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", FINANCE_MODULE_CODE] })
      toast.success(isEdit ? "Record updated" : "Record created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save record"
      toast.error(typeof detail === "string" ? detail : "Could not save record")
    },
  })

  if (!open) return null

  const loadingRecord = isEdit && recordQuery.isFetching
  const saving = saveMutation.isPending
  const showProgress = loadingRecord || saving
  const loadError = isEdit && recordQuery.isError

  const { register, handleSubmit, formState, setValue } = form

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-busy={showProgress}
    >
      <form
        className="my-4 flex w-full max-w-4xl flex-col rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values: FinanceFormValues) => saveMutation.mutate(values))}
      >
        <div className="border-b border-border px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold">
              {isEdit ? "Edit FI/CO record" : "New FI/CO record"}
            </h2>
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
          {showProgress ? <Progress indeterminate className="mt-3" /> : null}
        </div>

        <div className="max-h-[min(70vh,720px)] overflow-y-auto p-4">
          {loadError ? (
            <p className="text-sm text-destructive">Could not load this record. Try again.</p>
          ) : loadingRecord ? (
            <p className="py-12 text-center text-sm text-muted-foreground">Loading record…</p>
          ) : (
            <div className="space-y-6">
              <div className="grid gap-3 sm:grid-cols-2">
                <Field label="Feature area" error={formState.errors.feature_code?.message}>
                  <Select
                    {...register("feature_code")}
                    onChange={(e) => {
                      const next = e.target.value
                      setValue("feature_code", next)
                      const nextSections = getFinanceSectionsForFeature(next)
                      const hasLines = nextSections.some((s) => s.isLineItems)
                      if (hasLines && lineItemsArray.fields.length === 0) {
                        lineItemsArray.append(emptyLineItem())
                      }
                    }}
                  >
                    {FINANCE_FEATURE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </Select>
                </Field>
              </div>

              {sections.map((section) => (
                <section key={section.id} className="space-y-3">
                  <div>
                    <h3 className="text-sm font-semibold">{section.title}</h3>
                    {section.description ? (
                      <p className="text-xs text-muted-foreground">{section.description}</p>
                    ) : null}
                  </div>

                  {section.isLineItems ? (
                    <LineItemsEditor
                      fields={lineItemsArray.fields}
                      onAdd={() => lineItemsArray.append(emptyLineItem())}
                      onRemove={(index) => lineItemsArray.remove(index)}
                      register={register}
                    />
                  ) : (
                    <div className="grid gap-3 sm:grid-cols-2">
                      {section.fields.map((field) => (
                        <FinanceField
                          key={field.path}
                          field={field}
                          register={register}
                          error={
                            formState.errors as Record<string, { message?: string } | undefined>
                          }
                        />
                      ))}
                    </div>
                  )}
                </section>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={showProgress || loadError || (isEdit && !recordQuery.data)}
          >
            {saving ? "Saving…" : isEdit ? "Save changes" : "Create record"}
          </Button>
        </div>
      </form>
    </div>
  )
}

function FinanceField({
  field,
  register,
  error,
}: {
  field: FinanceFieldDef
  register: ReturnType<typeof useForm<FinanceFormValues>>["register"]
  error: Record<string, { message?: string } | undefined>
}) {
  const err = getNestedError(error, field.path)
  const spanClass = field.colSpan === 2 ? "sm:col-span-2" : ""

  return (
    <Field label={field.label} error={err} className={spanClass}>
      {field.type === "textarea" ? (
        <Textarea {...register(field.path as never)} rows={2} />
      ) : field.type === "select" && field.options ? (
        <Select {...register(field.path as never)}>
          {field.options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </Select>
      ) : (
        <Input
          {...register(field.path as never)}
          type={field.type === "number" ? "text" : field.type === "date" ? "date" : "text"}
          inputMode={field.type === "number" ? "decimal" : undefined}
          placeholder={field.placeholder}
        />
      )}
    </Field>
  )
}

function LineItemsEditor({
  fields,
  onAdd,
  onRemove,
  register,
}: {
  fields: { id: string }[]
  onAdd: () => void
  onRemove: (index: number) => void
  register: ReturnType<typeof useForm<FinanceFormValues>>["register"]
}) {
  return (
    <div className="space-y-4">
      {fields.length === 0 ? (
        <p className="text-xs text-muted-foreground">No line items yet. Add at least one line.</p>
      ) : null}
      {fields.map((row, index) => (
        <div
          key={row.id}
          className="rounded-lg border border-border/80 bg-muted/20 p-3 space-y-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Line {index + 1}</span>
            <Button type="button" variant="ghost" size="sm" onClick={() => onRemove(index)}>
              Remove
            </Button>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {lineItemFields.map((field) => (
              <Field key={field.path} label={field.label}>
                <Input
                  {...register(
                    `transactional.line_items.${index}.${field.path}` as never,
                  )}
                  type={field.type === "number" ? "text" : "text"}
                  inputMode={field.type === "number" ? "decimal" : undefined}
                />
              </Field>
            ))}
          </div>
        </div>
      ))}
      <Button type="button" variant="outline" size="sm" onClick={onAdd}>
        Add line item
      </Button>
    </div>
  )
}

function Field({
  label,
  error,
  children,
  className,
}: {
  label: string
  error?: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={className}>
      <Label className="mb-1 block text-xs">{label}</Label>
      {children}
      {error ? <p className="mt-1 text-xs text-destructive">{error}</p> : null}
    </div>
  )
}

function getNestedError(
  errors: Record<string, { message?: string } | undefined>,
  path: string,
): string | undefined {
  const parts = path.split(".")
  let cur: unknown = errors
  for (const part of parts) {
    if (!cur || typeof cur !== "object") return undefined
    cur = (cur as Record<string, unknown>)[part]
  }
  if (cur && typeof cur === "object" && "message" in cur) {
    return (cur as { message?: string }).message
  }
  return undefined
}
