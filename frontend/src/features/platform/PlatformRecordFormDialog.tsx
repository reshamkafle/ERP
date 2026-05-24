import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
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
  PLATFORM_CORE_FIELDS,
  PLATFORM_FORM_TABS,
  type PlatformFieldDef,
  type PlatformTabDef,
} from "@/lib/platform-field-groups"
import {
  defaultPlatformFormValues,
  formToCreatePayload,
  formToUpdatePayload,
  newPlatformReference,
  PLATFORM_MODULE_CODE,
  platformFormSchema,
  recordToForm,
  type PlatformFormValues,
} from "@/lib/platform-record-schema"
import { cn } from "@/lib/utils"

type Props = {
  open: boolean
  editingId: number | null
  defaultFeatureCode: string
  onClose: () => void
}

export function PlatformRecordFormDialog({
  open,
  editingId,
  defaultFeatureCode,
  onClose,
}: Props) {
  const queryClient = useQueryClient()
  const isEdit = editingId !== null
  const [activeTab, setActiveTab] = useState(PLATFORM_FORM_TABS[0]?.id ?? "identity")

  const recordQuery = useQuery({
    queryKey: ["erp-modules", PLATFORM_MODULE_CODE, "record", editingId],
    queryFn: () => fetchModuleRecord(PLATFORM_MODULE_CODE, editingId!),
    enabled: open && isEdit,
  })

  const form = useForm<PlatformFormValues>({
    resolver: zodResolver(platformFormSchema),
    defaultValues: defaultPlatformFormValues,
  })

  useEffect(() => {
    if (!open) return
    if (isEdit && recordQuery.data) {
      form.reset(recordToForm(recordQuery.data))
      setActiveTab("identity")
      return
    }
    if (!isEdit) {
      const ref = newPlatformReference()
      form.reset({
        ...defaultPlatformFormValues,
        feature_code: defaultFeatureCode || defaultPlatformFormValues.feature_code,
        reference: ref,
        title: "",
      })
      setActiveTab("identity")
    }
  }, [open, isEdit, recordQuery.data, defaultFeatureCode, form])

  const saveMutation = useMutation({
    mutationFn: async (values: PlatformFormValues) => {
      if (isEdit && editingId) {
        return updateModuleRecord(PLATFORM_MODULE_CODE, editingId, formToUpdatePayload(values))
      }
      return createModuleRecord(PLATFORM_MODULE_CODE, formToCreatePayload(values))
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", PLATFORM_MODULE_CODE] })
      toast.success(isEdit ? "Module record updated" : "Module record created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save module record"
      toast.error(typeof detail === "string" ? detail : "Could not save module record")
    },
  })

  if (!open) return null

  const loadingRecord = isEdit && recordQuery.isFetching
  const saving = saveMutation.isPending
  const showProgress = loadingRecord || saving
  const loadError = isEdit && recordQuery.isError

  const { register, handleSubmit, formState } = form
  const activeTabDef =
    PLATFORM_FORM_TABS.find((t) => t.id === activeTab) ?? PLATFORM_FORM_TABS[0]

  return (
    <DialogOverlay
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-6"
      role="dialog"
      ariaModal="true"
      ariaBusy={showProgress}
    >
      <form
        className="my-4 flex w-full max-w-4xl flex-col rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values: PlatformFormValues) => saveMutation.mutate(values))}
      >
        <div className="border-b border-border px-4 py-3">
          <DialogHeader isEdit={isEdit} onClose={onClose} showProgress={showProgress} />
        </div>

        <div className="border-b border-border px-4 py-3">
          <div className="grid gap-3 sm:grid-cols-2">
            {PLATFORM_CORE_FIELDS.map((field) => (
              <PlatformField
                key={field.path}
                field={field}
                register={register}
                error={formState.errors as Record<string, { message?: string } | undefined>}
              />
            ))}
          </div>
        </div>

        <div className="border-b border-border px-2 pt-2">
          <div className="flex flex-wrap gap-1 px-2 pb-2">
            {PLATFORM_FORM_TABS.map((tab) => (
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
            <p className="text-sm text-destructive">Could not load this record. Try again.</p>
          ) : loadingRecord ? (
            <p className="py-12 text-center text-sm text-muted-foreground">Loading record…</p>
          ) : (
            <TabPanel tab={activeTabDef} register={register} formState={formState} />
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
          {isEdit ? "Edit industry module" : "New industry module"}
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
}: {
  tab: PlatformTabDef
  register: ReturnType<typeof useForm<PlatformFormValues>>["register"]
  formState: ReturnType<typeof useForm<PlatformFormValues>>["formState"]
}) {
  return (
    <section className="space-y-3">
      <TabHeader tab={tab} />
      <div className="grid gap-3 sm:grid-cols-2">
        {(tab.fields ?? []).map((field) => (
          <PlatformField
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

function TabHeader({ tab }: { tab: PlatformTabDef }) {
  return (
    <div>
      <h3 className="text-sm font-semibold">{tab.title}</h3>
      {tab.description ? (
        <p className="text-xs text-muted-foreground">{tab.description}</p>
      ) : null}
    </div>
  )
}

function PlatformField({
  field,
  register,
  error,
}: {
  field: PlatformFieldDef
  register: ReturnType<typeof useForm<PlatformFormValues>>["register"]
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
  field: PlatformFieldDef
  register: ReturnType<typeof useForm<PlatformFormValues>>["register"]
}) {
  const path = field.path as Parameters<typeof register>[0]

  if (field.type === "textarea") {
    return <Textarea {...register(path)} rows={4} placeholder={field.placeholder} />
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
    field.type === "number" ? "number" : field.type === "date" ? "date" : "text"

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
