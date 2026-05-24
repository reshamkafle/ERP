export type ModuleFeatureDef = {
  code: string
  name: string
  description: string
}

export type ModuleDef = {
  code: string
  name: string
  short_name: string
  description: string
  route_path: string
  permission_read: string
  permission_write: string
  linked_routes: string[]
  features: ModuleFeatureDef[]
}

export type ModuleCatalogResponse = {
  modules: ModuleDef[]
}

export type ModuleFeatureCount = {
  code: string
  name: string
  description: string
  record_count: number
}

export type ModuleIntegrationMetric = {
  label: string
  value: string
  hint?: string | null
}

export type ModuleOverview = {
  module_code: string
  module_name: string
  description: string
  features: ModuleFeatureCount[]
  integration_metrics: ModuleIntegrationMetric[]
  total_records: number
}

export type ModuleRecord = {
  id: number
  module_code: string
  feature_code: string
  reference: string
  title: string
  status: string
  description: string | null
  party_name: string | null
  amount: string | null
  quantity: number | null
  start_date: string | null
  end_date: string | null
  extra_data: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export type ModuleRecordListResponse = {
  items: ModuleRecord[]
  total: number
}

export type ModuleRecordCreate = {
  feature_code: string
  reference: string
  title: string
  status?: string
  description?: string | null
  party_name?: string | null
  amount?: number | null
  quantity?: number | null
  start_date?: string | null
  end_date?: string | null
  extra_data?: Record<string, unknown> | null
}

export type ModuleRecordUpdate = {
  title?: string
  status?: string
  description?: string | null
  party_name?: string | null
  amount?: number | null
  quantity?: number | null
  start_date?: string | null
  end_date?: string | null
  extra_data?: Record<string, unknown> | null
}
