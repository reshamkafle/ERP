export type UserRole = "ADMIN" | "MANAGER" | "CASHIER"

export interface AuthUser {
  id: number
  email: string
  role: UserRole
  is_active: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export interface DashboardSummary {
  heading: string
  low_stock_count: number
  open_pos_sessions: number
}
