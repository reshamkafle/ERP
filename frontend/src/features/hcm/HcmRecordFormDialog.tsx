import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo } from "react"
import { useFieldArray, useForm, type Control, type UseFormRegister } from "react-hook-form"
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
  getHcmSectionsForFeature,
  HCM_FEATURE_OPTIONS,
  REPEATABLE_ARRAY_PATH,
  REPEATABLE_FIELD_MAP,
  type HcmFieldDef,
  type HcmRepeatableKey,
  type HcmSectionDef,
} from "@/lib/hcm-field-groups"
import {
  defaultHcmFormValues,
  emptyCertification,
  emptyDependent,
  emptyEmergencyContact,
  emptyInterviewScore,
  emptyInternalHistory,
  emptyLanguageSkill,
  emptyLeaveRequest,
  emptyPayrollLine,
  emptyPreviousEmployment,
  emptySalaryComponent,
  formToCreatePayload,
  formToUpdatePayload,
  HCM_MODULE_CODE,
  hcmFormSchema,
  newHcmReference,
  recordToForm,
  type HcmFormValues,
} from "@/lib/hcm-record-schema"

type Props = {
  open: boolean
  editingId: number | null
  defaultFeatureCode: string
  onClose: () => void
}

const EMPTY_BY_KEY: Record<HcmRepeatableKey, () => Record<string, string>> = {
  emergency_contacts: emptyEmergencyContact,
  salary_components: emptySalaryComponent,
  certifications: emptyCertification,
  language_skills: emptyLanguageSkill,
  previous_employment: emptyPreviousEmployment,
  internal_history: emptyInternalHistory,
  dependents: emptyDependent,
  payslip_elements: emptyPayrollLine,
  interview_scores: emptyInterviewScore,
  leave_requests: emptyLeaveRequest,
  training_certifications: emptyCertification,
  benefits_dependents: emptyDependent,
}

export function HcmRecordFormDialog({
  open,
  editingId,
  defaultFeatureCode,
  onClose,
}: Props) {
  const queryClient = useQueryClient()
  const isEdit = editingId !== null

  const recordQuery = useQuery({
    queryKey: ["erp-modules", HCM_MODULE_CODE, "record", editingId],
    queryFn: () => fetchModuleRecord(HCM_MODULE_CODE, editingId!),
    enabled: open && isEdit,
  })

  const form = useForm<HcmFormValues>({
    resolver: zodResolver(hcmFormSchema),
    defaultValues: defaultHcmFormValues,
  })

  const featureCode = form.watch("feature_code")
  const sections = useMemo(() => getHcmSectionsForFeature(featureCode), [featureCode])

  useEffect(() => {
    if (!open) return
    if (isEdit && recordQuery.data) {
      form.reset(recordToForm(recordQuery.data))
      return
    }
    if (!isEdit) {
      const fc = defaultFeatureCode || "employee_records"
      form.reset({
        ...defaultHcmFormValues,
        feature_code: fc,
        reference: newHcmReference(fc),
      })
    }
  }, [open, isEdit, recordQuery.data, defaultFeatureCode, form])

  const saveMutation = useMutation({
    mutationFn: async (values: HcmFormValues) => {
      if (isEdit && editingId) {
        return updateModuleRecord(HCM_MODULE_CODE, editingId, formToUpdatePayload(values))
      }
      return createModuleRecord(HCM_MODULE_CODE, formToCreatePayload(values))
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", HCM_MODULE_CODE] })
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
  const { register, handleSubmit, formState, setValue, control } = form

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-busy={showProgress}
    >
      <form
        className="my-4 flex w-full max-w-5xl flex-col rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values: HcmFormValues) => saveMutation.mutate(values))}
      >
        <div className="border-b border-border px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold">
              {isEdit ? "Edit HCM record" : "New HCM record"}
            </h2>
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
          {showProgress ? <Progress indeterminate className="mt-3" /> : null}
        </div>

        <div className="max-h-[min(75vh,800px)] overflow-y-auto p-4">
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
                    onChange={(e) => setValue("feature_code", e.target.value)}
                  >
                    {HCM_FEATURE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </Select>
                </Field>
              </div>

              {sections.map((section) => (
                <SectionBlock
                  key={section.id}
                  section={section}
                  register={register}
                  control={control}
                  errors={formState.errors as Record<string, { message?: string } | undefined>}
                />
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

function SectionBlock({
  section,
  register,
  control,
  errors,
}: {
  section: HcmSectionDef
  register: UseFormRegister<HcmFormValues>
  control: Control<HcmFormValues>
  errors: Record<string, { message?: string } | undefined>
}) {
  if (section.isRepeatable && section.repeatableKey) {
    return (
      <section className="space-y-3">
        <div>
          <h3 className="text-sm font-semibold">{section.title}</h3>
          {section.description ? (
            <p className="text-xs text-muted-foreground">{section.description}</p>
          ) : null}
        </div>
        <RepeatableEditor
          repeatableKey={section.repeatableKey}
          control={control}
          register={register}
        />
      </section>
    )
  }

  return (
    <section className="space-y-3">
      <div>
        <h3 className="text-sm font-semibold">{section.title}</h3>
        {section.description ? (
          <p className="text-xs text-muted-foreground">{section.description}</p>
        ) : null}
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {section.fields.map((field) => (
          <HcmField key={field.path} field={field} register={register} error={errors} />
        ))}
      </div>
    </section>
  )
}

function RepeatableEditor({
  repeatableKey,
  control,
  register,
}: {
  repeatableKey: HcmRepeatableKey
  control: Control<HcmFormValues>
  register: UseFormRegister<HcmFormValues>
}) {
  const arrayPath = REPEATABLE_ARRAY_PATH[repeatableKey] as keyof HcmFormValues & string
  const fieldDefs = REPEATABLE_FIELD_MAP[repeatableKey]
  const empty = EMPTY_BY_KEY[repeatableKey]

  const { fields, append, remove } = useFieldArray({
    control,
    name: arrayPath as never,
  })

  return (
    <div className="space-y-4">
      {fields.length === 0 ? (
        <p className="text-xs text-muted-foreground">No entries yet.</p>
      ) : null}
      {fields.map((row, index) => (
        <div
          key={row.id}
          className="space-y-3 rounded-lg border border-border/80 bg-muted/20 p-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Row {index + 1}</span>
            <Button type="button" variant="ghost" size="sm" onClick={() => remove(index)}>
              Remove
            </Button>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {fieldDefs.map((field) => (
              <Field key={field.path} label={field.label}>
                <Input
                  {...register(`${arrayPath}.${index}.${field.path}` as never)}
                  type={field.type === "date" ? "date" : "text"}
                />
              </Field>
            ))}
          </div>
        </div>
      ))}
      <Button type="button" variant="outline" size="sm" onClick={() => append(empty() as never)}>
        Add row
      </Button>
    </div>
  )
}

function HcmField({
  field,
  register,
  error,
}: {
  field: HcmFieldDef
  register: UseFormRegister<HcmFormValues>
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
          type={field.type === "date" ? "date" : "text"}
          inputMode={field.type === "number" ? "decimal" : undefined}
          placeholder={field.placeholder}
        />
      )}
    </Field>
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
