import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"
import axios from "axios"
import { useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api"
import type { AuthUser, LoginResponse } from "@/types/user"

interface AuthContextValue {
  user: AuthUser | null
  permissions: string[]
  isBootstrapping: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

async function fetchPermissions(): Promise<string[]> {
  const { data } = await api.get<{ permissions: string[] }>("/v1/auth/me/permissions")
  return data.permissions
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState<AuthUser | null>(null)
  const [permissions, setPermissions] = useState<string[]>([])
  const [isBootstrapping, setIsBootstrapping] = useState(true)

  const refreshUser = useCallback(async () => {
    try {
      const meRes = await api.get<AuthUser>("/v1/auth/me")
      setUser(meRes.data)
      try {
        setPermissions(await fetchPermissions())
      } catch {
        setPermissions([])
      }
    } catch {
      setUser(null)
      setPermissions([])
      throw new Error("not authenticated")
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        await refreshUser()
      } catch {
        setUser(null)
        setPermissions([])
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
    setUser(data.user)
    if (data.permissions?.length) {
      setPermissions(data.permissions)
      return
    }
    try {
      setPermissions(await fetchPermissions())
    } catch {
      setPermissions([])
    }
  }, [])

  const logout = useCallback(() => {
    void api.post("/v1/auth/logout").catch(() => undefined)
    queryClient.clear()
    setUser(null)
    setPermissions([])
  }, [queryClient])

  const value = useMemo(
    () => ({ user, permissions, isBootstrapping, login, logout, refreshUser }),
    [user, permissions, isBootstrapping, login, logout, refreshUser],
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

export function getLoginErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return "Cannot reach the server. Start Docker, Postgres, and the backend (port 8000)."
    }
    if (error.response.status === 401) {
      return "Invalid email or password."
    }
    if (error.response.status === 429) {
      const detail = error.response.data?.detail
      if (typeof detail === "string") {
        return detail
      }
      return "Too many login attempts. Please wait and try again."
    }
    const detail = error.response.data?.detail
    if (typeof detail === "string") {
      return detail
    }
  }
  return "Sign-in failed. Please try again."
}
