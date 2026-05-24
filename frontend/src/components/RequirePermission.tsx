import { Navigate } from "react-router-dom"

import { useAuth } from "@/context/AuthContext"
import { canAccess, canAccessAny } from "@/lib/permissions"

type RequirePermissionProps = {
  permission?: string
  anyOf?: string[]
  children: React.ReactNode
}

export function RequirePermission({ permission, anyOf, children }: RequirePermissionProps) {
  const { permissions, isBootstrapping } = useAuth()

  if (isBootstrapping) {
    return null
  }

  const allowed = permission
    ? canAccess(permissions, permission)
    : anyOf
      ? canAccessAny(permissions, anyOf)
      : true

  if (!allowed) {
    return <Navigate to="/forbidden" replace />
  }

  return <>{children}</>
}
