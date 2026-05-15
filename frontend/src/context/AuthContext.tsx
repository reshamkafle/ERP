import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"

import { api } from "@/lib/api"
import { clearToken, getToken, setToken as persistToken } from "@/lib/auth-storage"
import type { AuthUser, LoginResponse } from "@/types/user"

interface AuthContextValue {
  user: AuthUser | null
  isBootstrapping: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isBootstrapping, setIsBootstrapping] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = getToken()
    if (!token) {
      setUser(null)
      return
    }
    const { data } = await api.get<AuthUser>("/v1/auth/me")
    setUser(data)
  }, [])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        if (getToken()) {
          await refreshUser()
        }
      } catch {
        clearToken()
        setUser(null)
      } finally {
        if (!cancelled) {
          setIsBootstrapping(false)
        }
      }
    })()
    return () => {
      cancelled = true
    }
  }, [refreshUser])

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await api.post<LoginResponse>("/v1/auth/login", { email, password })
    persistToken(data.access_token)
    setUser(data.user)
  }, [])

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, isBootstrapping, login, logout, refreshUser }),
    [user, isBootstrapping, login, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return ctx
}
