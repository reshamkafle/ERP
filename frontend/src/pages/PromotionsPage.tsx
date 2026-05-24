import { useEffect, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  confirmPromotionRun,
  createPromotionRun,
  fetchPromotionRun,
} from "@/features/promotions/promotions-api"
import type { PromotionProject } from "@/types/promotion"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"

function cloneProjects(projects: PromotionProject[]): PromotionProject[] {
  return JSON.parse(JSON.stringify(projects)) as PromotionProject[]
}

function getErrorDetail(err: unknown): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: unknown }).msg)
        }
        return String(item)
      })
      .join("; ")
  }
  const message = (err as { message?: string })?.message
  return message && message !== "Network Error" ? message : "Request failed"
}

export function PromotionsPage() {
    const queryClient = useQueryClient()
  const [runId, setRunId] = useState<number | null>(null)
  const [draftProjects, setDraftProjects] = useState<PromotionProject[]>([])
  const [lookback, setLookback] = useState(30)
  const [maxAnchors, setMaxAnchors] = useState(15)
  const [maxRelated, setMaxRelated] = useState(5)

  const detailQuery = useQuery({
    queryKey: ["promotion-runs", runId],
    queryFn: () => fetchPromotionRun(runId!),
    enabled: runId != null,
  })

  useEffect(() => {
    const d = detailQuery.data
    if (d == null || d.id !== runId) return
    if (d.status !== "DRAFT_REVIEW" || !d.proposals_json?.projects?.length) return
    setDraftProjects((prev) => {
      if (prev.length > 0) return prev
      return cloneProjects(d.proposals_json!.projects)
    })
  }, [detailQuery.data, runId])

  const runMutation = useMutation({
    mutationFn: () =>
      createPromotionRun({
        sales_lookback_days: lookback,
        max_anchor_products: maxAnchors,
        max_related_per_anchor: maxRelated,
        max_projects: 25,
      }),
    onSuccess: (data) => {
      setRunId(data.id)
      setDraftProjects([])
      void queryClient.invalidateQueries({ queryKey: ["promotion-runs", data.id] })
      toast.success("Promotion agent finished — review proposals below.")
      if (data.warnings.length) {
        toast.message(`${data.warnings.length} signal warning(s)`, {
          description: data.warnings.slice(0, 5).join("\n"),
        })
      }
    },
    onError: (err: unknown) => {
      toast.error(getErrorDetail(err))
    },
  })

  const confirmMutation = useMutation({
    mutationFn: (payload: { reject: boolean }) =>
      confirmPromotionRun(runId!, {
        reject: payload.reject,
        projects: payload.reject ? [] : draftProjects,
      }),
    onSuccess: (data) => {
      void queryClient.invalidateQueries({ queryKey: ["promotion-runs", data.id] })
      toast.success(
        data.status === "APPROVED"
          ? "Promotion plan approved and saved."
          : data.status === "REJECTED"
            ? "Promotion run rejected."
            : "Updated.",
      )
    },
    onError: (err: unknown) => {
      toast.error(getErrorDetail(err))
    },
  })

  const detail = detailQuery.data
  const proposals = detail?.proposals_json
  const canConfirm =
    runId != null && detail?.status === "DRAFT_REVIEW" && draftProjects.length > 0

  const updateLine = (
    projectIndex: number,
    lineIndex: number,
    field: "discount_percent" | "duration_days",
    raw: string,
  ) => {
    setDraftProjects((prev) => {
      const next = cloneProjects(prev)
      const line = next[projectIndex]?.related_items[lineIndex]
      if (!line) return prev
      if (field === "discount_percent") {
        const n = Number(raw)
        line.discount_percent = Number.isFinite(n) ? n : line.discount_percent
      } else {
        const n = parseInt(raw, 10)
        line.duration_days = Number.isFinite(n) ? n : line.duration_days
      }
      return next
    })
  }

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <PageHeader
        title="Promotions"
        description="Multi-agent workflow proposes related-item bundles with discount and duration. Approved plans are stored for ops; POS checkout is unchanged in this version."
      />

      <ContentSheet className="space-y-4">
      <section className="rounded-md border border-border bg-muted/30 p-4">
        <h2 className="text-lg font-semibold text-foreground">Run promotion agent</h2>
        <p className="mb-4 text-sm text-muted-foreground">
          Uses recent sales for anchors and co-purchase affinity plus category / product-line
          neighbors.
        </p>
        <div className="mb-4 flex flex-wrap gap-4">
          <div className="space-y-1">
            <Label htmlFor="lookback">Sales lookback (days)</Label>
            <Input
              id="lookback"
              type="number"
              min={1}
              max={365}
              className="w-32"
              value={lookback}
              onChange={(e) => setLookback(Number(e.target.value) || 30)}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="anchors">Max anchor products</Label>
            <Input
              id="anchors"
              type="number"
              min={1}
              max={200}
              className="w-32"
              value={maxAnchors}
              onChange={(e) => setMaxAnchors(Number(e.target.value) || 15)}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="related">Max related per anchor</Label>
            <Input
              id="related"
              type="number"
              min={1}
              max={30}
              className="w-32"
              value={maxRelated}
              onChange={(e) => setMaxRelated(Number(e.target.value) || 5)}
            />
          </div>
        </div>
        <Button type="button" disabled={runMutation.isPending} onClick={() => runMutation.mutate()}>
          {runMutation.isPending ? "Running…" : "Generate promotion proposals"}
        </Button>
        {runId != null ? (
          <p className="mt-2 text-xs text-muted-foreground">Current run id: {runId}</p>
        ) : null}
      </section>

      {detailQuery.isLoading && runId != null ? (
        <p className="text-sm text-muted-foreground">Loading run…</p>
      ) : null}

      {detail?.status === "FAILED" ? (
        <div className="rounded-md border border-destructive/50 bg-destructive/5 p-3 text-sm text-destructive">
          Run failed: {detail.error_message ?? "Unknown error"}
        </div>
      ) : null}

      {proposals && detail?.status === "DRAFT_REVIEW" ? (
        <section className="space-y-3 rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-semibold text-foreground">Proposed promotion projects</h2>
            {proposals.fallback_used ? (
              <Badge variant="secondary">Rule-based / fallback merge</Badge>
            ) : (
              <Badge variant="default">LLM-assisted</Badge>
            )}
          </div>
          {proposals.merge_notes ? (
            <p className="text-sm text-muted-foreground">{proposals.merge_notes}</p>
          ) : null}
          {draftProjects.length === 0 ? (
            <p className="text-sm text-muted-foreground">No projects in this run.</p>
          ) : (
            <div className="space-y-6">
              {draftProjects.map((proj, pi) => (
                <div
                  key={proj.project_id || pi}
                  className="rounded-md border border-border bg-background p-3"
                >
                  <div className="mb-2 text-sm font-medium text-foreground">
                    Project: {proj.project_id}
                  </div>
                  <p className="mb-2 text-xs text-muted-foreground">
                    Anchor:{" "}
                    <span className="text-foreground">
                      {(proj.anchor?.sku as string) ?? ""} — {(proj.anchor?.name as string) ?? ""}{" "}
                      (#{String(proj.anchor?.product_id ?? "")})
                    </span>
                  </p>
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[520px] border-collapse text-left text-sm">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground">
                          <th className="py-2 pr-2 font-medium">SKU</th>
                          <th className="py-2 pr-2 font-medium">Name</th>
                          <th className="py-2 pr-2 font-medium">Discount %</th>
                          <th className="py-2 pr-2 font-medium">Duration (days)</th>
                          <th className="py-2 font-medium">Note</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(proj.related_items ?? []).map((line, li) => (
                          <tr key={`${line.product_id}-${li}`} className="border-b border-border/80">
                            <td className="py-2 pr-2">{line.sku}</td>
                            <td className="py-2 pr-2">{line.name}</td>
                            <td className="py-2 pr-2">
                              <Input
                                className="h-8 w-20"
                                type="number"
                                min={0}
                                max={100}
                                step={1}
                                value={line.discount_percent ?? ""}
                                onChange={(e) => updateLine(pi, li, "discount_percent", e.target.value)}
                              />
                            </td>
                            <td className="py-2 pr-2">
                              <Input
                                className="h-8 w-24"
                                type="number"
                                min={1}
                                max={365}
                                value={line.duration_days ?? 14}
                                onChange={(e) => updateLine(pi, li, "duration_days", e.target.value)}
                              />
                            </td>
                            <td className="max-w-xs truncate py-2 text-xs text-muted-foreground">
                              {line.rationale}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="flex flex-wrap gap-2 pt-2">
            <Button
              type="button"
              disabled={!canConfirm || confirmMutation.isPending}
              onClick={() => confirmMutation.mutate({ reject: false })}
            >
              Confirm promotion plan
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={runId == null || detail?.status !== "DRAFT_REVIEW" || confirmMutation.isPending}
              onClick={() => confirmMutation.mutate({ reject: true })}
            >
              Reject
            </Button>
          </div>
        </section>
      ) : null}

      {detail?.status === "APPROVED" || detail?.status === "REJECTED" ? (
        <section className="rounded-lg border border-border bg-muted/30 p-4 text-sm">
          <p className="font-medium text-foreground">Run closed — status: {detail.status}</p>
          {detail.approved_json?.projects?.length ? (
            <p className="mt-1 text-muted-foreground">
              {detail.approved_json.projects.length} project(s) saved in approved_json.
            </p>
          ) : null}
        </section>
      ) : null}
      </ContentSheet>
    </div>
    </PosOnlyRedirect>
  )
}