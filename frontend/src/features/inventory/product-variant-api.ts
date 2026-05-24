import { api } from "@/lib/api"
import type {
  MatrixGenerateRequest,
  MatrixGenerateResult,
  ProductAttribute,
  ProductTemplate,
  ProductTemplateListResponse,
  TemplateVariantsResponse,
} from "@/types/product-variant"
import type { ItemType } from "@/types/inventory"

export type ProductTemplateCreatePayload = {
  style_code: string
  name: string
  description?: string | null
  sku_prefix: string
  category_id?: number | null
  item_type?: ItemType
  product_line?: string | null
  primary_uom?: string
  default_price?: number
  default_cost_price?: number
  image_url?: string | null
  manufacturing_item_sku?: string | null
  is_active?: boolean
}

export async function fetchProductAttributes() {
  const { data } = await api.get<ProductAttribute[]>("/v1/inventory/attributes")
  return data
}

export async function fetchProductTemplates(params?: {
  search?: string
  is_active?: boolean
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<ProductTemplateListResponse>("/v1/inventory/templates", {
    params,
  })
  return data
}

export async function fetchProductTemplate(id: number) {
  const { data } = await api.get<ProductTemplate>(`/v1/inventory/templates/${id}`)
  return data
}

export async function createProductTemplate(payload: ProductTemplateCreatePayload) {
  const { data } = await api.post<ProductTemplate>("/v1/inventory/templates", payload)
  return data
}

export async function fetchTemplateVariants(templateId: number) {
  const { data } = await api.get<TemplateVariantsResponse>(
    `/v1/inventory/templates/${templateId}/variants`,
  )
  return data
}

export async function generateVariantMatrix(templateId: number, body: MatrixGenerateRequest) {
  const { data } = await api.post<MatrixGenerateResult>(
    `/v1/inventory/templates/${templateId}/generate-matrix`,
    body,
  )
  return data
}
