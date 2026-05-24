import { Navigate } from "react-router-dom"

import { useAuth } from "@/context/AuthContext"
import { isPosOnlyUser } from "@/lib/permissions"

type PosOnlyRedirectProps = {
  children: React.ReactNode
}

/** Redirect POS-only users away from back-office pages. */
export function PosOnlyRedirect({ children }: PosOnlyRedirectProps) {
  const { permissions, isBootstrapping } = useAuth()
  if (isBootstrapping) {
    return null
  }
  if (isPosOnlyUser(permissions)) {
    return <Navigate to="/pos" replace />
  }
  return <>{children}</>
}
