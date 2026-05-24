import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo, useState } from "react"
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
  getScmSectionsForFeature,
  SCM_FEATURE_OPTIONS,
  type ScmFieldDef,
} from "@/lib/scm-field-groups"
import {
  defaultScmFormValues,
  emptyScmLineItem,
  formToCreatePayload,
  formToUpdatePayload,
  newScmReference,
  SCM_MODULE_CODE,
  scmFormCompletionPercent,
  scmFormSchema,
  recordToForm,
  type ScmFormValues,
} from "@/lib/scm-record-schema"
import { cn } from "@/lib/utils"

type Props = {
  open: boolean
  editingId: number | null
  defaultFeatureCode: string
  onClose: () => void
}

export function ScmRecordFormDialog({
  open,
  editingId,
  defaultFeatureCode,
  onClose,
}: Props) {
  const queryClient = useQueryClient()
  const isEdit = editingId !== null
  const [activeTab, setActiveTab] = useState("core")

  const recordQuery = useQuery({
    queryKey: ["erp-modules", SCM_MODULE_CODE, "record", editingId],
    queryFn: () => fetchModuleRecord(SCM_MODULE_CODE, editingId!),
    enabled: open && isEdit,
  })

  const form = useForm<ScmFormValues>({
    resolver: zodResolver(scmFormSchema),
    defaultValues: defaultScmFormValues,
  })

  const featureCode = form.watch("feature_code")
  const sections = useMemo(() => getScmSectionsForFeature(featureCode), [featureCode])
  const watched = form.watch()

  const completionPct = useMemo(() => scmFormCompletionPercent(watched), [watched])

  const lineItemsArray = useFieldArray({
    control: form.control,
    name: "line_items",
  })

  const activeSection = sections.find((s) => s.id === activeTab) ?? sections[0]

  useEffect(() => {
    if (!open) return
    if (isEdit && recordQuery.data) {
      form.reset(recordToForm(recordQuery.data))
      setActiveTab("core")
      return
    }
    if (!isEdit) {
      const feature = defaultFeatureCode || "demand_planning"
      form.reset({
        ...defaultScmFormValues,
        feature_code: feature,
        reference: newScmReference(feature),
        line_items: [],
      })
      setActiveTab("core")
    }
  }, [open, isEdit, recordQuery.data, defaultFeatureCode, form])

  const saveMutation = useMutation({
    mutationFn: async (values: ScmFormValues) => {
      if (isEdit && editingId) {
        return updateModuleRecord(SCM_MODULE_CODE, editingId, formToUpdatePayload(values))
      }
      return createModuleRecord(SCM_MODULE_CODE, formToCreatePayload(values))
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", SCM_MODULE_CODE] })
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

  const { register, handleSubmit, formState } = form

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-busy={showProgress}
    >
      <form
        className="my-4 flex w-full max-w-4xl flex-col rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values: ScmFormValues) => saveMutation.mutate(values))}
      >
        <div className="border-b border-border px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold">
              {isEdit ? "Edit SCM record" : "New SCM record"}
            </h2>
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
          <div className="mt-2 flex items-center gap-3">
            <Progress value={completionPct} className="h-1.5 flex-1" />
            <span className="text-xs tabular-nums text-muted-foreground">{completionPct}%</span>
          </div>
          {showProgress ? <Progress indeterminate className="mt-2" /> : null}
        </div>

        <div className="border-b border-border px-4 py-2">
          <div className="flex flex-wrap gap-1">
            {sections.map((section) => (
              <button
                key={section.id}
                type="button"
                onClick={() => setActiveTab(section.id)}
                className={cn(
                  "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                  activeTab === section.id
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80",
                )}
              >
                {section.title}
              </button>
            ))}
          </div>
        </div>

        <div className="max-h-[min(65vh,640px)] overflow-y-auto p-4">
          {loadError ? (
            <p className="text-sm text-destructive">Could not load this record. Try again.</p>
          ) : loadingRecord ? (
            <p className="py-12 text-center text-sm text-muted-foreground">Loading record…</p>
          ) : (
            <div className="space-y-4">
              {activeTab === "core" ? (
                <Field label="Record type" error={formState.errors.feature_code?.message}>
                  <Select {...register("feature_code")}>
                    {SCM_FEATURE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </Select>
                </Field>
              ) : null}

              <section className="space-y-3">
                <div>
                  <h3 className="text-sm font-semibold">{activeSection.title}</h3>
                  {activeSection.description ? (
                    <p className="text-xs text-muted-foreground">{activeSection.description}</p>
                  ) : null}
                </div>

                {activeSection.isLineItems ? (
                  <LineItemsEditor
                    fields={lineItemsArray.fields}
                    lineFields={activeSection.fields}
                    onAdd={() => lineItemsArray.append(emptyScmLineItem())}
                    onRemove={(index) => lineItemsArray.remove(index)}
                    register={register}
                  />
                ) : (
                  <div className="grid gap-3 sm:grid-cols-2">
                    {activeSection.fields.map((field) => (
                      <ScmField
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

function ScmField({
  field,
  register,
  error,
}: {
  field: ScmFieldDef
  register: ReturnType<typeof useForm<ScmFormValues>>["register"]
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
            <option key={opt.value || "none"} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </Select>
      ) : (
        <Input
          {...register(field.path as never)}
          type={field.type === "date" ? "date" : field.type === "number" ? "text" : "text"}
          inputMode={field.type === "number" ? "decimal" : undefined}
          placeholder={field.placeholder}
        />
      )}
    </Field>
  )
}

function LineItemsEditor({
  fields,
  lineFields,
  onAdd,
  onRemove,
  register,
}: {
  fields: { id: string }[]
  lineFields: ScmFieldDef[]
  onAdd: () => void
  onRemove: (index: number) => void
  register: ReturnType<typeof useForm<ScmFormValues>>["register"]
}) {
  return (
    <div className="space-y-4">
      {fields.length === 0 ? (
        <p className="text-xs text-muted-foreground">No line items yet. Add lines as needed.</p>
      ) : null}
      {fields.map((row, index) => (
        <div
          key={row.id}
          className="space-y-3 rounded-lg border border-border/80 bg-muted/20 p-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Line {index + 1}</span>
            <Button type="button" variant="ghost" size="sm" onClick={() => onRemove(index)}>
              Remove
            </Button>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {lineFields.map((field) => (
              <Field
                key={field.path}
                label={field.label}
                className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
              >
                <Input
                  {...register(`line_items.${index}.${field.path}` as never)}
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
