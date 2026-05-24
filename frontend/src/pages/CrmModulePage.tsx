import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { CrmLeadFormDialog, CrmOpportunityFormDialog } from "@/features/crm/CrmPipelineDialogs"
import { CrmRecordFormDialog } from "@/features/crm/CrmRecordFormDialog"
import { CustomerFormDialog } from "@/features/customers/CustomerFormDialog"
import {
  deleteLead,
  deleteOpportunity,
  fetchCrmContacts,
  fetchLeads,
  fetchOpportunities,
  fetchPipelineSummary,
} from "@/features/crm/crm-api"
import {
  deleteModuleRecord,
  fetchModuleOverview,
  fetchModuleRecords,
} from "@/features/modules/modules-api"
import { useAuth } from "@/context/AuthContext"
import { CRM_MODULE_CODE } from "@/lib/crm-record-schema"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"
import type { Customer } from "@/types/customer"
import type { CrmLead, CrmOpportunity } from "@/types/crm"
import type { ModuleRecord } from "@/types/module"

const MODULE_RECORD_FEATURES = new Set([
  "marketing_campaigns",
  "customer_service",
  "support_tickets",
])

export function CrmModulePage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [feature, setFeature] = useState<string>("sales_pipeline")
  const [pipelineTab, setPipelineTab] = useState<"leads" | "opportunities">("leads")
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingRecordId, setEditingRecordId] = useState<number | null>(null)
  const [editingLead, setEditingLead] = useState<CrmLead | null>(null)
  const [editingOpp, setEditingOpp] = useState<CrmOpportunity | null>(null)
  const [leadDialogOpen, setLeadDialogOpen] = useState(false)
  const [oppDialogOpen, setOppDialogOpen] = useState(false)
  const [customerAccountOpen, setCustomerAccountOpen] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null)

  const canWrite = canAccess(permissions, "crm.records.write")
  const canCustomersWrite = canAccess(permissions, "sales.customers.write")
  const canLeadsWrite = canAccess(permissions, "crm.leads.write")
  const canOppsWrite = canAccess(permissions, "crm.opportunities.write")

  const overviewQuery = useQuery({
    queryKey: ["erp-modules", CRM_MODULE_CODE, "overview"],
    queryFn: () => fetchModuleOverview(CRM_MODULE_CODE),
  })

  const pipelineQuery = useQuery({
    queryKey: ["crm", "pipeline"],
    queryFn: fetchPipelineSummary,
  })

  const leadsQuery = useQuery({
    queryKey: ["crm", "leads", search],
    queryFn: () => fetchLeads({ search: search || undefined }),
    enabled: feature === "sales_pipeline" && pipelineTab === "leads",
  })

  const oppsQuery = useQuery({
    queryKey: ["crm", "opportunities", search],
    queryFn: () => fetchOpportunities({ search: search || undefined }),
    enabled: feature === "sales_pipeline" && pipelineTab === "opportunities",
  })

  const contactsQuery = useQuery({
    queryKey: ["crm", "contacts", search],
    queryFn: () => fetchCrmContacts({ search: search || undefined }),
    enabled: feature === "contacts",
  })

  const recordsQuery = useQuery({
    queryKey: ["erp-modules", CRM_MODULE_CODE, "records", feature, search],
    queryFn: () =>
      fetchModuleRecords(CRM_MODULE_CODE, {
        feature_code: feature,
        search: search || undefined,
      }),
    enabled: MODULE_RECORD_FEATURES.has(feature),
  })

  const deleteRecordMutation = useMutation({
    mutationFn: (id: number) => deleteModuleRecord(CRM_MODULE_CODE, id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", CRM_MODULE_CODE] })
      toast.success("Record deleted")
    },
  })

  const deleteLeadMutation = useMutation({
    mutationFn: deleteLead,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["crm", "leads"] })
      toast.success("Lead deleted")
    },
  })

  const deleteOppMutation = useMutation({
    mutationFn: deleteOpportunity,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["crm", "opportunities"] })
      toast.success("Opportunity deleted")
    },
  })

  const features = overviewQuery.data?.features ?? []

  const defaultFeatureCode = useMemo(() => {
    if (MODULE_RECORD_FEATURES.has(feature)) return feature
    return "marketing_campaigns"
  }, [feature])

  return (
    <div className="space-y-4">
      <PageHeader
        title="Customer Relationship Management"
        description="Pipeline, contacts, marketing, and support — integrated with customer master data."
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {canCustomersWrite ? (
              <Button
                type="button"
                size="sm"
                onClick={() => {
                  setEditingCustomer(null)
                  setCustomerAccountOpen(true)
                }}
              >
                New account
              </Button>
            ) : null}
            <Link to="/customers" className="text-sm text-primary hover:underline">
              Customer master →
            </Link>
          </div>
        }
      />

      {pipelineQuery.data ? (
        <ContentSheet>
          <div className="flex flex-wrap gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Open leads: </span>
              <span className="font-medium">{pipelineQuery.data.open_lead_count}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Pipeline value: </span>
              <span className="font-medium tabular-nums">
                {Number(pipelineQuery.data.total_open_value).toLocaleString()}
              </span>
            </div>
          </div>
        </ContentSheet>
      ) : null}

      <ControlPanel className="flex flex-wrap items-center gap-2">
        {features.map((f) => (
          <Button
            key={f.code}
            type="button"
            size="sm"
            variant={feature === f.code ? "default" : "outline"}
            onClick={() => setFeature(f.code)}
          >
            {f.name}
          </Button>
        ))}
        <Input
          className="max-w-xs"
          placeholder="Search…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {feature === "sales_pipeline" ? (
          <>
            <Button
              type="button"
              size="sm"
              variant={pipelineTab === "leads" ? "default" : "ghost"}
              onClick={() => setPipelineTab("leads")}
            >
              Leads
            </Button>
            <Button
              type="button"
              size="sm"
              variant={pipelineTab === "opportunities" ? "default" : "ghost"}
              onClick={() => setPipelineTab("opportunities")}
            >
              Opportunities
            </Button>
            {canLeadsWrite && pipelineTab === "leads" ? (
              <Button
                type="button"
                size="sm"
                onClick={() => {
                  setEditingLead(null)
                  setLeadDialogOpen(true)
                }}
              >
                Add lead
              </Button>
            ) : null}
            {canOppsWrite && pipelineTab === "opportunities" ? (
              <Button
                type="button"
                size="sm"
                onClick={() => {
                  setEditingOpp(null)
                  setOppDialogOpen(true)
                }}
              >
                Add opportunity
              </Button>
            ) : null}
          </>
        ) : MODULE_RECORD_FEATURES.has(feature) && canWrite ? (
          <Button
            type="button"
            size="sm"
            onClick={() => {
              setEditingRecordId(null)
              setDialogOpen(true)
            }}
          >
            Add record
          </Button>
        ) : null}
      </ControlPanel>

      <ContentSheet className="overflow-x-auto p-0">
        {feature === "sales_pipeline" && pipelineTab === "leads" ? (
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2">Company</th>
                <th className="px-3 py-2">Contact</th>
                <th className="px-3 py-2">Source</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {(leadsQuery.data?.items ?? []).map((lead) => (
                <tr key={lead.id} className="border-b border-border/60">
                  <td className="px-3 py-2 font-medium">{lead.company_name}</td>
                  <td className="px-3 py-2 text-muted-foreground">{lead.contact_name ?? "—"}</td>
                  <td className="px-3 py-2">{lead.source ?? "—"}</td>
                  <td className="px-3 py-2">
                    <Badge variant="secondary">{lead.status}</Badge>
                  </td>
                  <td className="px-3 py-2 text-right">
                    {canLeadsWrite ? (
                      <>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditingLead(lead)
                            setLeadDialogOpen(true)
                          }}
                        >
                          Edit
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="text-destructive"
                          onClick={() => {
                            if (window.confirm("Delete lead?")) deleteLeadMutation.mutate(lead.id)
                          }}
                        >
                          Delete
                        </Button>
                      </>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}

        {feature === "sales_pipeline" && pipelineTab === "opportunities" ? (
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2">Title</th>
                <th className="px-3 py-2">Stage</th>
                <th className="px-3 py-2">Probability</th>
                <th className="px-3 py-2">Value</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {(oppsQuery.data?.items ?? []).map((opp) => (
                <tr key={opp.id} className="border-b border-border/60">
                  <td className="px-3 py-2">
                    <Link
                      to={`/customers/${opp.customer_id}`}
                      className="font-medium text-primary hover:underline"
                    >
                      {opp.title}
                    </Link>
                  </td>
                  <td className="px-3 py-2">
                    <Badge>{opp.stage}</Badge>
                  </td>
                  <td className="px-3 py-2">{opp.probability}%</td>
                  <td className="px-3 py-2 tabular-nums">
                    {opp.expected_value ? Number(opp.expected_value).toLocaleString() : "—"}
                  </td>
                  <td className="px-3 py-2 text-right">
                    {canOppsWrite ? (
                      <>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditingOpp(opp)
                            setOppDialogOpen(true)
                          }}
                        >
                          Edit
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="text-destructive"
                          onClick={() => {
                            if (window.confirm("Delete opportunity?")) deleteOppMutation.mutate(opp.id)
                          }}
                        >
                          Delete
                        </Button>
                      </>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}

        {feature === "contacts" ? (
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2">Name</th>
                <th className="px-3 py-2">Role</th>
                <th className="px-3 py-2">Customer</th>
                <th className="px-3 py-2">Influence</th>
              </tr>
            </thead>
            <tbody>
              {(contactsQuery.data ?? []).map((c) => (
                <tr key={c.id} className="border-b border-border/60">
                  <td className="px-3 py-2 font-medium">{c.name}</td>
                  <td className="px-3 py-2">{c.role ?? "—"}</td>
                  <td className="px-3 py-2">
                    <Link
                      to={`/customers/${c.customer_id}`}
                      className="text-primary hover:underline"
                    >
                      View account #{c.customer_id}
                    </Link>
                  </td>
                  <td className="px-3 py-2">{c.influence_level ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}

        {MODULE_RECORD_FEATURES.has(feature) ? (
          <ModuleRecordsTable
            records={recordsQuery.data?.items ?? []}
            canWrite={canWrite}
            onEdit={(id) => {
              setEditingRecordId(id)
              setDialogOpen(true)
            }}
            onDelete={(id) => {
              if (window.confirm("Delete record?")) deleteRecordMutation.mutate(id)
            }}
          />
        ) : null}
      </ContentSheet>

      <CrmRecordFormDialog
        open={dialogOpen}
        editingId={editingRecordId}
        defaultFeatureCode={defaultFeatureCode}
        onClose={() => {
          setDialogOpen(false)
          setEditingRecordId(null)
        }}
      />
      <CrmLeadFormDialog
        open={leadDialogOpen}
        lead={editingLead}
        onClose={() => {
          setLeadDialogOpen(false)
          setEditingLead(null)
        }}
      />
      <CrmOpportunityFormDialog
        open={oppDialogOpen}
        opportunity={editingOpp}
        onClose={() => {
          setOppDialogOpen(false)
          setEditingOpp(null)
        }}
      />
      <CustomerFormDialog
        open={customerAccountOpen}
        customer={editingCustomer}
        onClose={() => {
          setCustomerAccountOpen(false)
          setEditingCustomer(null)
          void queryClient.invalidateQueries({ queryKey: ["customers"] })
        }}
      />
    </div>
  )
}

function ModuleRecordsTable({
  records,
  canWrite,
  onEdit,
  onDelete,
}: {
  records: ModuleRecord[]
  canWrite: boolean
  onEdit: (id: number) => void
  onDelete: (id: number) => void
}) {
  return (
    <table className="w-full min-w-[640px] text-left text-sm">
      <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
        <tr>
          <th className="px-3 py-2">Reference</th>
          <th className="px-3 py-2">Title</th>
          <th className="px-3 py-2">Status</th>
          <th className="px-3 py-2 text-right">Actions</th>
        </tr>
      </thead>
      <tbody>
        {records.map((r) => (
          <tr key={r.id} className="border-b border-border/60">
            <td className="px-3 py-2 font-mono text-xs">{r.reference}</td>
            <td className="px-3 py-2">{r.title}</td>
            <td className="px-3 py-2">
              <Badge variant="secondary">{r.status}</Badge>
            </td>
            <td className="px-3 py-2 text-right">
              {canWrite ? (
                <>
                  <Button type="button" variant="ghost" size="sm" onClick={() => onEdit(r.id)}>
                    Edit
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className={cn("text-destructive")}
                    onClick={() => onDelete(r.id)}
                  >
                    Delete
                  </Button>
                </>
              ) : null}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
