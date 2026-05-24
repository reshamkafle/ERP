import { api } from "@/lib/api"

export type SearchEntityType =
  | "customer"
  | "sale"
  | "erp_document"
  | "purchase"
  | "production_order"
  | "supplier"
  | "product"
  | "material_roll"
  | "warehouse"
  | "storage_location"
  | "module_record"
  | "crm_lead"
  | "crm_opportunity"
  | "crm_contact"

export type SearchGroup =
  | "pages"
  | "sales"
  | "procurement"
  | "manufacturing"
  | "inventory"
  | "modules"
  | "crm"

export type SearchHit = {
  entity_type: SearchEntityType
  entity_id: number
  title: string
  subtitle: string | null
  route: string
  group: SearchGroup
  highlights: string[]
  related: {
    entity_type: SearchEntityType
    entity_id: number
    title: string
    route: string
  }[]
}

export type SearchResponse = {
  query: string
  results: SearchHit[]
}

export async function fetchGlobalSearch(params: {
  q: string
  limit?: number
  types?: SearchEntityType[]
  saleId?: number
}): Promise<SearchResponse> {
  const { data } = await api.get<SearchResponse>("/v1/search", {
    params: {
      q: params.q,
      limit: params.limit ?? 20,
      types: params.types,
      sale_id: params.saleId,
    },
  })
  return data
}

export const SEARCH_ENTITY_LABELS: Record<SearchEntityType, string> = {
  customer: "Customer",
  sale: "Sales order",
  erp_document: "Document",
  purchase: "Purchase order",
  production_order: "Production order",
  supplier: "Supplier",
  product: "Product",
  material_roll: "Fabric roll",
  warehouse: "Warehouse",
  storage_location: "Storage location",
  module_record: "Module record",
  crm_lead: "Lead",
  crm_opportunity: "Opportunity",
  crm_contact: "Contact",
}
