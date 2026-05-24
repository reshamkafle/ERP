import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate, useParams } from "react-router-dom"

import { ContentSheet } from "@/components/ContentSheet"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { deleteCustomerContact } from "@/features/crm/crm-api"
import { ActivityFormDialog } from "@/features/crm/ActivityFormDialog"
import { ContactFormDialog } from "@/features/crm/ContactFormDialog"
import { CustomerFormDialog } from "@/features/customers/CustomerFormDialog"
import {
  fetchCustomer,
  fetchCustomerActivities,
  fetchCustomerAuditLog,
  fetchCustomerContacts,
  fetchCustomerDocuments,
  fetchCustomerOpportunities,
  fetchCustomerOverview,
} from "@/features/customers/customers-api"
import { useAuth } from "@/context/AuthContext"
import { CUSTOMER_TABS } from "@/lib/customer-field-groups"
import { formatMoney } from "@/lib/format-money"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"
import type { Customer } from "@/types/customer"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"

function ReadOnlySection({ customer, tabId }: { customer: Customer; tabId: string }) {
  const tab = CUSTOMER_TABS.find((t) => t.id === tabId)
  if (!tab) return null
  const val = (key: keyof Customer) => {
    const v = customer[key]
    if (v === null || v === undefined || v === "") return "—"
    return String(v)
  }
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {tab.fields.map((f) => (
        <div key={f.path} className={f.colSpan === 2 ? "sm:col-span-2" : ""}>
          <p className="text-xs uppercase text-muted-foreground">{f.label}</p>
          <p className="text-sm">{val(f.path as keyof Customer)}</p>
        </div>
      ))}
    </div>
  )
}

export function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [activeTab, setActiveTab] = useState("overview")
  const [contactDialogOpen, setContactDialogOpen] = useState(false)
  const [editingContact, setEditingContact] = useState<import("@/types/crm").CustomerContact | null>(null)
  const [activityDialogOpen, setActivityDialogOpen] = useState(false)
  const [editingActivity, setEditingActivity] = useState<import("@/types/crm").CrmActivity | null>(null)
  const customerId = Number(id)

  const canContacts = canAccess(permissions, "crm.contacts.write")
  const canActivities = canAccess(permissions, "crm.activities.write")

  const detailQuery = useQuery({
    queryKey: ["customers", "detail", customerId],
    queryFn: () => fetchCustomer(customerId),
    enabled: Number.isFinite(customerId) && customerId > 0,
  })

  const overviewQuery = useQuery({
    queryKey: ["customers", "overview", customerId],
    queryFn: () => fetchCustomerOverview(customerId),
    enabled: Number.isFinite(customerId) && customerId > 0,
  })

  const contactsQuery = useQuery({
    queryKey: ["customers", customerId, "contacts"],
    queryFn: () => fetchCustomerContacts(customerId),
    enabled: activeTab === "contacts" && customerId > 0,
  })

  const activitiesQuery = useQuery({
    queryKey: ["customers", customerId, "activities"],
    queryFn: () => fetchCustomerActivities(customerId),
    enabled: activeTab === "activities" && customerId > 0,
  })

  const oppsQuery = useQuery({
    queryKey: ["customers", customerId, "opportunities"],
    queryFn: () => fetchCustomerOpportunities(customerId),
    enabled: activeTab === "opportunities" && customerId > 0,
  })

  const documentsQuery = useQuery({
    queryKey: ["customers", customerId, "documents"],
    queryFn: () => fetchCustomerDocuments(customerId),
    enabled: activeTab === "documents" && customerId > 0,
  })

  const auditQuery = useQuery({
    queryKey: ["customers", customerId, "audit"],
    queryFn: () => fetchCustomerAuditLog(customerId),
    enabled: activeTab === "audit" && customerId > 0,
  })

  if (!Number.isFinite(customerId) || customerId <= 0) {
    return <Navigate to="/customers" replace />
  }

  if (detailQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading customer…</p>
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-destructive">Customer not found.</p>
        <Link to="/customers" className="text-sm text-primary hover:underline">
          Back to customers
        </Link>
      </div>
    )
  }

  const customer = detailQuery.data
  const sales = customer.recent_sales
  const overview = overviewQuery.data

  const detailTabs = [
    { id: "overview", label: "Overview" },
    { id: "financial", label: "Financial & ERP" },
    { id: "profile", label: "Profile" },
    { id: "company", label: "Company" },
    { id: "commercial", label: "Commercial" },
    { id: "tax", label: "Tax" },
    { id: "contacts", label: "Contacts" },
    { id: "activities", label: "Activities" },
    { id: "opportunities", label: "Opportunities" },
    { id: "sales", label: "Sales" },
    { id: "documents", label: "Attachments" },
    { id: "audit", label: "Audit trail" },
  ]

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/customers" className="text-sm text-muted-foreground hover:text-foreground">
            ← Customers
          </Link>
          <h1 className="mt-2 text-xl font-semibold text-foreground">{customer.name}</h1>
          <p className="text-sm text-muted-foreground">
            {customer.customer_code ? `${customer.customer_code} · ` : ""}
            {customer.segment ? (
              <Badge variant="secondary" className="ml-1">
                {customer.segment}
              </Badge>
            ) : null}
          </p>
        </div>
        <Button type="button" onClick={() => setDialogOpen(true)}>
          Edit customer
        </Button>
      </div>

      <div className="flex flex-wrap gap-1">
        {detailTabs.map((t) => (
          <button
            key={t.id}
            type="button"
            className={cn(
              "rounded-md px-3 py-1.5 text-sm",
              activeTab === t.id
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted",
            )}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && overview ? (
        <ContentSheet>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Metric label="Lifetime value" value={formatMoney(overview.lifetime_value)} />
            <Metric label="Revenue YTD" value={formatMoney(overview.revenue_ytd)} />
            <Metric label="Open balance" value={formatMoney(overview.open_balance)} />
            <Metric label="Sales orders" value={String(overview.sale_count)} />
            <Metric label="Open opportunities" value={String(overview.open_opportunity_count)} />
            <Metric label="Pipeline value" value={formatMoney(overview.open_opportunity_value)} />
            <Metric label="Contacts" value={String(overview.contact_count)} />
            <Metric label="Activities" value={String(overview.activity_count)} />
            <Metric label="Documents" value={String(overview.document_count)} />
            <Metric label="Payments" value={String(overview.payment_count)} />
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Created {new Date(customer.created_at).toLocaleString()} · Updated{" "}
            {new Date(customer.updated_at).toLocaleString()}
          </p>
        </ContentSheet>
      ) : null}

      {activeTab === "financial" && overview ? (
        <ContentSheet>
          <p className="mb-3 text-xs text-muted-foreground">
            Computed from sales and payments (read-only).
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Metric label="Total lifetime value" value={formatMoney(overview.lifetime_value)} />
            <Metric label="All-time revenue" value={formatMoney(overview.total_revenue)} />
            <Metric label="Revenue YTD" value={formatMoney(overview.revenue_ytd)} />
            <Metric label="Revenue last year" value={formatMoney(overview.revenue_last_year)} />
            <Metric label="Open receivables" value={formatMoney(overview.open_receivables)} />
            <Metric label="Average order value" value={formatMoney(overview.average_order_value)} />
            <Metric
              label="Purchase frequency / year"
              value={Number(overview.purchase_frequency_per_year).toFixed(2)}
            />
            <Metric
              label="Last purchase"
              value={
                overview.last_purchase_date
                  ? new Date(overview.last_purchase_date).toLocaleDateString()
                  : "—"
              }
            />
            <Metric label="Payment count" value={String(overview.payment_count)} />
          </div>
        </ContentSheet>
      ) : null}

      {["profile", "company", "commercial", "tax"].includes(activeTab) ? (
        <ContentSheet>
          <ReadOnlySection customer={customer} tabId={activeTab === "profile" ? "profile" : activeTab} />
          {activeTab === "profile" ? (
            <>
              <hr className="my-4 border-border" />
              <ReadOnlySection customer={customer} tabId="contacts" />
            </>
          ) : null}
          {activeTab === "commercial" ? (
            <>
              <hr className="my-4 border-border" />
              <ReadOnlySection customer={customer} tabId="billing" />
              <hr className="my-4 border-border" />
              <ReadOnlySection customer={customer} tabId="shipping" />
            </>
          ) : null}
        </ContentSheet>
      ) : null}

      {activeTab === "contacts" ? (
        <ContentSheet className="space-y-4">
          {canContacts ? (
            <Button
              type="button"
              size="sm"
              onClick={() => {
                setEditingContact(null)
                setContactDialogOpen(true)
              }}
            >
              Add contact
            </Button>
          ) : null}
          <ul className="space-y-2 text-sm">
            {(contactsQuery.data ?? []).map((c) => (
              <li key={c.id} className="flex items-center justify-between rounded border border-border px-3 py-2">
                <div>
                  <span className="font-medium">{c.name}</span>
                  {c.is_primary ? (
                    <Badge className="ml-2" variant="default">
                      Primary
                    </Badge>
                  ) : null}
                  <p className="text-xs text-muted-foreground">
                    {[c.role, c.email, c.phone].filter(Boolean).join(" · ") || "—"}
                  </p>
                </div>
                {canContacts ? (
                  <div className="flex gap-1">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setEditingContact(c)
                        setContactDialogOpen(true)
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
                        if (window.confirm(`Remove ${c.name}?`)) {
                          void deleteCustomerContact(customerId, c.id).then(() => {
                            void queryClient.invalidateQueries({
                              queryKey: ["customers", customerId, "contacts"],
                            })
                          })
                        }
                      }}
                    >
                      Remove
                    </Button>
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        </ContentSheet>
      ) : null}

      {activeTab === "activities" ? (
        <ContentSheet className="space-y-4">
          {canActivities ? (
            <Button
              type="button"
              size="sm"
              onClick={() => {
                setEditingActivity(null)
                setActivityDialogOpen(true)
              }}
            >
              Log activity
            </Button>
          ) : null}
          <ul className="space-y-2 text-sm">
            {(activitiesQuery.data ?? []).map((a) => (
              <li key={a.id} className="rounded border border-border px-3 py-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="secondary">{a.activity_type}</Badge>
                    <span className="font-medium">{a.subject}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(a.occurred_at).toLocaleString()}
                    </span>
                    {a.duration_minutes != null ? (
                      <span className="text-xs text-muted-foreground">{a.duration_minutes} min</span>
                    ) : null}
                  </div>
                  {canActivities ? (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setEditingActivity(a)
                        setActivityDialogOpen(true)
                      }}
                    >
                      Edit
                    </Button>
                  ) : null}
                </div>
                {a.outcome ? <p className="mt-1 text-xs">Outcome: {a.outcome}</p> : null}
                {a.body ? <p className="mt-1 text-muted-foreground">{a.body}</p> : null}
                {a.next_follow_up_at ? (
                  <p className="mt-1 text-xs text-muted-foreground">
                    Next follow-up: {new Date(a.next_follow_up_at).toLocaleString()}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        </ContentSheet>
      ) : null}

      {activeTab === "opportunities" ? (
        <ContentSheet>
          <table className="w-full text-left text-sm">
            <thead className="text-xs uppercase text-muted-foreground">
              <tr>
                <th className="py-2">Title</th>
                <th className="py-2">Stage</th>
                <th className="py-2">Value</th>
                <th className="py-2">History</th>
              </tr>
            </thead>
            <tbody>
              {(oppsQuery.data?.items ?? []).map((o) => (
                <tr key={o.id} className="border-t border-border">
                  <td className="py-2">{o.title}</td>
                  <td className="py-2">
                    <Badge>{o.stage}</Badge>
                  </td>
                  <td className="py-2 tabular-nums">
                    {o.expected_value ? formatMoney(o.expected_value) : "—"}
                  </td>
                  <td className="py-2 text-xs text-muted-foreground">
                    {(o.stage_history ?? []).length > 0
                      ? o.stage_history!.map((h) => `${h.from_stage ?? "—"} → ${h.to_stage}`).join("; ")
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Link to="/crm" className="mt-3 inline-block text-sm text-primary hover:underline">
            Manage pipeline in CRM →
          </Link>
        </ContentSheet>
      ) : null}

      {activeTab === "documents" ? (
        <ContentSheet>
          <p className="mb-3 text-xs text-muted-foreground">
            Linked ERP documents (contracts, agreements). Upload files via Documents module.
          </p>
          <ul className="space-y-2 text-sm">
            {(documentsQuery.data?.items ?? []).length === 0 ? (
              <li className="text-muted-foreground">No linked documents.</li>
            ) : (
              (documentsQuery.data?.items ?? []).map((d) => (
                <li key={d.id} className="flex items-center justify-between rounded border border-border px-3 py-2">
                  <div>
                    <span className="font-mono text-xs">{d.document_number}</span>
                    <span className="ml-2 font-medium">{d.title}</span>
                  </div>
                  <Badge variant="secondary">{d.status}</Badge>
                </li>
              ))
            )}
          </ul>
        </ContentSheet>
      ) : null}

      {activeTab === "audit" ? (
        <ContentSheet>
          <ul className="space-y-2 text-sm">
            {(auditQuery.data ?? []).length === 0 ? (
              <li className="text-muted-foreground">No changes recorded yet.</li>
            ) : (
              (auditQuery.data ?? []).map((entry) => (
                <li key={entry.id} className="rounded border border-border px-3 py-2">
                  <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <span>{new Date(entry.created_at).toLocaleString()}</span>
                    <Badge variant="secondary">{entry.field_name}</Badge>
                  </div>
                  <p className="mt-1">{entry.change_summary ?? "—"}</p>
                </li>
              ))
            )}
          </ul>
        </ContentSheet>
      ) : null}

      {activeTab === "sales" ? (
        <ContentSheet className="space-y-3">
          <div className="overflow-x-auto rounded-md border border-border">
            <table className="w-full min-w-[480px] text-left text-sm">
              <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 font-medium">Order</th>
                  <th className="px-3 py-2 font-medium">Date</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {sales.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                      No sales yet.
                    </td>
                  </tr>
                ) : (
                  sales.map((sale) => (
                    <tr key={sale.id} className="border-b border-border last:border-0">
                      <td className="px-3 py-2">
                        <Link
                          to={`/sales/${sale.id}`}
                          className="font-mono text-xs text-primary hover:underline"
                        >
                          {sale.order_number}
                        </Link>
                      </td>
                      <td className="px-3 py-2 text-muted-foreground">
                        {new Date(sale.created_at).toLocaleString()}
                      </td>
                      <td className="px-3 py-2">{sale.order_status}</td>
                      <td className="px-3 py-2 text-right tabular-nums font-medium">
                        {formatMoney(sale.total)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </ContentSheet>
      ) : null}

      <CustomerFormDialog
        open={dialogOpen}
        customer={customer}
        onClose={() => {
          setDialogOpen(false)
          void queryClient.invalidateQueries({ queryKey: ["customers", "detail", customerId] })
        }}
      />
      <ContactFormDialog
        open={contactDialogOpen}
        customerId={customerId}
        contact={editingContact}
        onClose={() => setContactDialogOpen(false)}
      />
      <ActivityFormDialog
        open={activityDialogOpen}
        customerId={customerId}
        activity={editingActivity}
        onClose={() => setActivityDialogOpen(false)}
      />
    </div>
    </PosOnlyRedirect>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold tabular-nums">{value}</p>
    </div>
  )
}