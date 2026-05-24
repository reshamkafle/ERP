export type UserRole = "ADMIN" | "MANAGER" | "CASHIER"

export interface AuthUser {
  id: number
  email: string
  role: UserRole
  is_active: boolean
}

export interface LoginResponse {
  user: AuthUser
  permissions?: string[]
}

export interface DashboardSummary {
  heading: string
  low_stock_count: number
  open_pos_sessions: number
}
