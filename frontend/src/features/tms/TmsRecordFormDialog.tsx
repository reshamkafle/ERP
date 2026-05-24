import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Trash2 } from "lucide-react"
import { useEffect, useState } from "react"
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
  TMS_FORM_TABS,
  type TmsFieldDef,
  type TmsTabDef,
} from "@/lib/tms-field-groups"
import {
  defaultTmsFormValues,
  emptyTmsLineItem,
  formToCreatePayload,
  formToUpdatePayload,
  newTmsReference,
  recordToForm,
  TMS_MODULE_CODE,
  tmsFormSchema,
  tmsLineFields,
  type TmsFormValues,
} from "@/lib/tms-record-schema"
import { cn } from "@/lib/utils"

type Props = {
  open: boolean
  editingId: number | null
  onClose: () => void
}

export function TmsRecordFormDialog({ open, editingId, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = editingId !== null
  const [activeTab, setActiveTab] = useState(TMS_FORM_TABS[0]?.id ?? "basic")

  const recordQuery = useQuery({
    queryKey: ["erp-modules", TMS_MODULE_CODE, "record", editingId],
    queryFn: () => fetchModuleRecord(TMS_MODULE_CODE, editingId!),
    enabled: open && isEdit,
  })

  const form = useForm<TmsFormValues>({
    resolver: zodResolver(tmsFormSchema),
    defaultValues: defaultTmsFormValues,
  })

  const lineItemsArray = useFieldArray({
    control: form.control,
    name: "line_items",
  })

  useEffect(() => {
    if (!open) return
    if (isEdit && recordQuery.data) {
      form.reset(recordToForm(recordQuery.data))
      setActiveTab("basic")
      return
    }
    if (!isEdit) {
      const ref = newTmsReference()
      form.reset({
        ...defaultTmsFormValues,
        reference: ref,
        title: "New shipment",
        basic: { ...defaultTmsFormValues.basic, shipment_id: ref },
      })
      setActiveTab("basic")
    }
  }, [open, isEdit, recordQuery.data, form])

  const saveMutation = useMutation({
    mutationFn: async (values: TmsFormValues) => {
      if (isEdit && editingId) {
        return updateModuleRecord(TMS_MODULE_CODE, editingId, formToUpdatePayload(values))
      }
      return createModuleRecord(TMS_MODULE_CODE, formToCreatePayload(values))
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", TMS_MODULE_CODE] })
      toast.success(isEdit ? "Shipment updated" : "Shipment created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save shipment"
      toast.error(typeof detail === "string" ? detail : "Could not save shipment")
    },
  })

  if (!open) return null

  const loadingRecord = isEdit && recordQuery.isFetching
  const saving = saveMutation.isPending
  const showProgress = loadingRecord || saving
  const loadError = isEdit && recordQuery.isError

  const { register, handleSubmit, formState } = form
  const activeTabDef = TMS_FORM_TABS.find((t) => t.id === activeTab) ?? TMS_FORM_TABS[0]
  const lineFields = tmsLineFields()

  return (
    <DialogOverlay
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-6"
      role="dialog"
      ariaModal="true"
      ariaBusy={showProgress}
    >
      <form
        className="my-4 flex w-full max-w-4xl flex-col rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values: TmsFormValues) => saveMutation.mutate(values))}
      >
        <div className="border-b border-border px-4 py-3">
          <DialogHeader isEdit={isEdit} onClose={onClose} showProgress={showProgress} />
        </div>

        <div className="border-b border-border px-2 pt-2">
          <div className="flex flex-wrap gap-1 px-2 pb-2">
            {TMS_FORM_TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                  activeTab === tab.id
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80",
                )}
              >
                {tab.title}
              </button>
            ))}
          </div>
        </div>

        <div className="max-h-[min(65vh,680px)] overflow-y-auto p-4">
          {loadError ? (
            <p className="text-sm text-destructive">Could not load this shipment. Try again.</p>
          ) : loadingRecord ? (
            <p className="py-12 text-center text-sm text-muted-foreground">Loading shipment…</p>
          ) : (
            <TabPanel
              tab={activeTabDef}
              register={register}
              formState={formState}
              lineItemsArray={lineItemsArray}
              lineFields={lineFields}
            />
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
            {saving ? "Saving…" : isEdit ? "Save changes" : "Create shipment"}
          </Button>
        </div>
      </form>
    </DialogOverlay>
  )
}

function DialogOverlay({
  className,
  role,
  ariaModal,
  ariaBusy,
  children,
}: {
  className?: string
  role?: string
  ariaModal?: boolean | "true" | "false"
  ariaBusy?: boolean
  children: React.ReactNode
}) {
  return (
    <div className={className} role={role} aria-modal={ariaModal} aria-busy={ariaBusy}>
      {children}
    </div>
  )
}

function DialogHeader({
  isEdit,
  onClose,
  showProgress,
}: {
  isEdit: boolean
  onClose: () => void
  showProgress: boolean
}) {
  return (
    <>
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">
          {isEdit ? "Edit shipment" : "New shipment"}
        </h2>
        <Button type="button" variant="ghost" size="sm" onClick={onClose}>
          Close
        </Button>
      </div>
      {showProgress ? <Progress indeterminate className="mt-3" /> : null}
    </>
  )
}

function TabPanel({
  tab,
  register,
  formState,
  lineItemsArray,
  lineFields,
}: {
  tab: TmsTabDef
  register: ReturnType<typeof useForm<TmsFormValues>>["register"]
  formState: ReturnType<typeof useForm<TmsFormValues>>["formState"]
  lineItemsArray: ReturnType<typeof useFieldArray<TmsFormValues, "line_items">>
  lineFields: TmsFieldDef[]
}) {
  if (tab.isLineItems) {
    return (
      <section className="space-y-3">
        <TabHeader tab={tab} />
        <LineItemsEditor
          fields={lineItemsArray.fields}
          lineFields={lineFields}
          onAdd={() => lineItemsArray.append(emptyTmsLineItem())}
          onRemove={(index) => lineItemsArray.remove(index)}
          register={register}
        />
      </section>
    )
  }

  return (
    <section className="space-y-3">
      <TabHeader tab={tab} />
      <div className="grid gap-3 sm:grid-cols-2">
        {(tab.fields ?? []).map((field) => (
          <TmsField
            key={field.path}
            field={field}
            register={register}
            error={formState.errors as Record<string, { message?: string } | undefined>}
          />
        ))}
      </div>
    </section>
  )
}

function TabHeader({ tab }: { tab: TmsTabDef }) {
  return (
    <div>
      <h3 className="text-sm font-semibold">{tab.title}</h3>
      {tab.description ? (
        <p className="text-xs text-muted-foreground">{tab.description}</p>
      ) : null}
    </div>
  )
}

function TmsField({
  field,
  register,
  error,
}: {
  field: TmsFieldDef
  register: ReturnType<typeof useForm<TmsFormValues>>["register"]
  error: Record<string, { message?: string } | undefined>
}) {
  const err = getNestedError(error, field.path)
  const spanClass = field.colSpan === 2 ? "sm:col-span-2" : ""

  return (
    <Field label={field.label} error={err} className={spanClass}>
      <FieldInput field={field} register={register} />
    </Field>
  )
}

function FieldInput({
  field,
  register,
}: {
  field: TmsFieldDef
  register: ReturnType<typeof useForm<TmsFormValues>>["register"]
}) {
  const path = field.path as Parameters<typeof register>[0]

  if (field.type === "checkbox") {
    return (
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" {...register(path)} />
        {field.label}
      </label>
    )
  }

  if (field.type === "textarea") {
    return <Textarea {...register(path)} rows={3} placeholder={field.placeholder} />
  }

  if (field.type === "select" && field.options) {
    return (
      <Select {...register(path)}>
        {field.options.map((opt) => (
          <option key={opt.value || "none"} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </Select>
    )
  }

  const inputType =
    field.type === "number"
      ? "number"
      : field.type === "date"
        ? "date"
        : field.type === "datetime-local"
          ? "datetime-local"
          : "text"

  return (
    <Input
      type={inputType}
      {...register(path)}
      placeholder={field.placeholder}
      inputMode={field.type === "number" ? "decimal" : undefined}
    />
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
  lineFields: TmsFieldDef[]
  onAdd: () => void
  onRemove: (index: number) => void
  register: ReturnType<typeof useForm<TmsFormValues>>["register"]
}) {
  return (
    <LineItemsList
      fields={fields}
      lineFields={lineFields}
      onAdd={onAdd}
      onRemove={onRemove}
      register={register}
    />
  )
}

function LineItemsList({
  fields,
  lineFields,
  onAdd,
  onRemove,
  register,
}: {
  fields: { id: string }[]
  lineFields: TmsFieldDef[]
  onAdd: () => void
  onRemove: (index: number) => void
  register: ReturnType<typeof useForm<TmsFormValues>>["register"]
}) {
  return (
    <div className="space-y-4">
      {fields.length === 0 ? (
        <p className="text-xs text-muted-foreground">No line items yet. Add at least one line.</p>
      ) : null}
      {fields.map((row, index) => (
        <div
          key={row.id}
          className="space-y-3 rounded-lg border border-border/80 bg-muted/20 p-3"
        >
          <LineItemHeader index={index} onRemove={onRemove} />
          <div className="grid gap-3 sm:grid-cols-2">
            {lineFields.map((field) => (
              <Field
                key={field.path}
                label={field.label}
                className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
              >
                <FieldInput
                  field={{ ...field, path: `line_items.${index}.${field.path}` }}
                  register={register}
                />
              </Field>
            ))}
          </div>
        </div>
      ))}
      <Button type="button" variant="outline" size="sm" onClick={onAdd}>
        <Plus className="mr-1 size-3.5" aria-hidden />
        Add line item
      </Button>
    </div>
  )
}

function LineItemHeader({
  index,
  onRemove,
}: {
  index: number
  onRemove: (index: number) => void
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs font-medium text-muted-foreground">Line {index + 1}</span>
      <Button type="button" variant="ghost" size="sm" onClick={() => onRemove(index)}>
        <Trash2 className="mr-1 size-3.5" aria-hidden />
        Remove
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
