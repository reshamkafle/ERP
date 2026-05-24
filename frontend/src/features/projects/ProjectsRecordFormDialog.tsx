import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Trash2 } from "lucide-react"
import { useEffect, useState } from "react"
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
  PROJECT_FORM_TABS,
  REPEATABLE_FIELD_MAP,
  type ProjectsFieldDef,
  type ProjectsRepeatableKey,
  type ProjectsTabDef,
} from "@/lib/projects-field-groups"
import {
  defaultProjectsFormValues,
  EMPTY_BY_REPEATABLE_KEY,
  formToCreatePayload,
  formToUpdatePayload,
  newProjectReference,
  PROJECTS_MODULE_CODE,
  projectsFormSchema,
  recordToForm,
  REPEATABLE_ARRAY_PATH,
  type ProjectsFormValues,
} from "@/lib/projects-record-schema"
import { cn } from "@/lib/utils"

type Props = {
  open: boolean
  editingId: number | null
  onClose: () => void
}

export function ProjectsRecordFormDialog({ open, editingId, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = editingId !== null
  const [activeTab, setActiveTab] = useState(PROJECT_FORM_TABS[0]?.id ?? "master_data")

  const recordQuery = useQuery({
    queryKey: ["erp-modules", PROJECTS_MODULE_CODE, "record", editingId],
    queryFn: () => fetchModuleRecord(PROJECTS_MODULE_CODE, editingId!),
    enabled: open && isEdit,
  })

  const form = useForm<ProjectsFormValues>({
    resolver: zodResolver(projectsFormSchema),
    defaultValues: defaultProjectsFormValues,
  })

  useEffect(() => {
    if (!open) return
    if (isEdit && recordQuery.data) {
      form.reset(recordToForm(recordQuery.data))
      setActiveTab("master_data")
      return
    }
    if (!isEdit) {
      const ref = newProjectReference()
      form.reset({
        ...defaultProjectsFormValues,
        reference: ref,
        title: "New project",
        master_data: {
          ...defaultProjectsFormValues.master_data,
          project_code: ref,
        },
      })
      setActiveTab("master_data")
    }
  }, [open, isEdit, recordQuery.data, form])

  const saveMutation = useMutation({
    mutationFn: async (values: ProjectsFormValues) => {
      if (isEdit && editingId) {
        return updateModuleRecord(PROJECTS_MODULE_CODE, editingId, formToUpdatePayload(values))
      }
      return createModuleRecord(PROJECTS_MODULE_CODE, formToCreatePayload(values))
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", PROJECTS_MODULE_CODE] })
      toast.success(isEdit ? "Project updated" : "Project created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save project"
      toast.error(typeof detail === "string" ? detail : "Could not save project")
    },
  })

  if (!open) return null

  const loadingRecord = isEdit && recordQuery.isFetching
  const saving = saveMutation.isPending
  const showProgress = loadingRecord || saving
  const loadError = isEdit && recordQuery.isError

  const { register, handleSubmit, formState, control } = form
  const activeTabDef = PROJECT_FORM_TABS.find((t) => t.id === activeTab) ?? PROJECT_FORM_TABS[0]

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-busy={showProgress}
    >
      <form
        className="my-4 flex w-full max-w-4xl flex-col rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values: ProjectsFormValues) => saveMutation.mutate(values))}
      >
        <div className="border-b border-border px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold">{isEdit ? "Edit project" : "New project"}</h2>
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
          {showProgress ? <Progress indeterminate className="mt-3" /> : null}
        </div>

        <div className="border-b border-border px-2 pt-2">
          <div className="flex flex-wrap gap-1 px-2 pb-2">
            {PROJECT_FORM_TABS.map((tab) => (
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
            <p className="text-sm text-destructive">Could not load this project. Try again.</p>
          ) : loadingRecord ? (
            <p className="py-12 text-center text-sm text-muted-foreground">Loading project…</p>
          ) : (
            <TabPanel
              tab={activeTabDef}
              register={register}
              control={control}
              formState={formState}
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
            {saving ? "Saving…" : isEdit ? "Save changes" : "Create project"}
          </Button>
        </div>
      </form>
    </div>
  )
}

function TabPanel({
  tab,
  register,
  control,
  formState,
}: {
  tab: ProjectsTabDef
  register: UseFormRegister<ProjectsFormValues>
  control: Control<ProjectsFormValues>
  formState: ReturnType<typeof useForm<ProjectsFormValues>>["formState"]
}) {
  return (
    <section className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold">{tab.title}</h3>
        {tab.description ? (
          <p className="text-xs text-muted-foreground">{tab.description}</p>
        ) : null}
      </div>

      {tab.fields?.length ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {tab.fields.map((field) => (
            <ProjectsField
              key={field.path}
              field={field}
              register={register}
              error={formState.errors as Record<string, { message?: string } | undefined>}
            />
          ))}
        </div>
      ) : null}

      {tab.repeatables?.map((rep) => (
        <RepeatableBlock
          key={rep.key}
          repeatableKey={rep.key}
          title={rep.title}
          rowLabel={rep.rowLabel}
          control={control}
          register={register}
        />
      ))}
    </section>
  )
}

function RepeatableBlock({
  repeatableKey,
  title,
  rowLabel,
  control,
  register,
}: {
  repeatableKey: ProjectsRepeatableKey
  title: string
  rowLabel: string
  control: Control<ProjectsFormValues>
  register: UseFormRegister<ProjectsFormValues>
}) {
  const arrayPath = REPEATABLE_ARRAY_PATH[repeatableKey]
  const fieldDefs = REPEATABLE_FIELD_MAP[repeatableKey]
  const empty = EMPTY_BY_REPEATABLE_KEY[repeatableKey]

  const { fields, append, remove } = useFieldArray({
    control,
    name: arrayPath as never,
  })

  return (
    <div className="space-y-3">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {title}
      </h4>
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
              <span className="text-xs font-medium text-muted-foreground">
                {rowLabel} {index + 1}
              </span>
              <Button type="button" variant="ghost" size="sm" onClick={() => remove(index)}>
                <Trash2 className="mr-1 size-3.5" aria-hidden />
                Remove
              </Button>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {fieldDefs.map((field) => (
                <Field
                  key={field.path}
                  label={field.label}
                  className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
                >
                  <FieldInput
                    field={{ ...field, path: `${arrayPath}.${index}.${field.path}` }}
                    register={register}
                  />
                </Field>
              ))}
            </div>
          </div>
        ))}
        <Button type="button" variant="outline" size="sm" onClick={() => append(empty() as never)}>
          <Plus className="mr-1 size-3.5" aria-hidden />
          Add {rowLabel.toLowerCase()}
        </Button>
      </div>
    </div>
  )
}

function ProjectsField({
  field,
  register,
  error,
}: {
  field: ProjectsFieldDef
  register: UseFormRegister<ProjectsFormValues>
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
  field: ProjectsFieldDef
  register: UseFormRegister<ProjectsFormValues>
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
