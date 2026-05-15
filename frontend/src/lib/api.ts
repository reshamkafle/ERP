import axios from "axios"

import { clearToken, getToken } from "@/lib/auth-storage"

export const api = axios.create({
  baseURL: "/api",
})

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken()
      if (!window.location.pathname.startsWith("/login")) {
        window.location.assign("/login")
      }
    }
    return Promise.reject(error)
  },
)
