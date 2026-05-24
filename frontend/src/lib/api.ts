import axios from "axios"

import { CSRF_COOKIE, CSRF_HEADER } from "@/lib/csrf"

export const api = axios.create({
  baseURL: "/api",
  timeout: 30_000,
  withCredentials: true,
})

function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : null
}

api.interceptors.request.use((config) => {
  const method = config.method?.toLowerCase()
  if (method && !["get", "head", "options"].includes(method)) {
    const csrf = readCookie(CSRF_COOKIE)
    if (csrf) {
      config.headers.set(CSRF_HEADER, csrf)
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      if (!window.location.pathname.startsWith("/login")) {
        try {
          await api.post("/v1/auth/logout")
        } catch {
          // ignore — cookie may already be cleared
        }
        window.location.assign("/login")
      }
    }
    return Promise.reject(error)
  },
)
