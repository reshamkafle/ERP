import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { canAccess } from "@/lib/permissions"

type Permission = { id: number; code: string; name: string; module: string }
type Role = {
  id: number
  name: string
  role_type: string
  department: string | null
  is_system: boolean
  permission_codes: string[]
}

export function AccessControlPage() {
  const { permissions: myPerms } = useAuth()
  const queryClient = useQueryClient()
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null)
  const [draftCodes, setDraftCodes] = useState<string[]>([])

  const { data: allPermissions = [] } = useQuery({
    queryKey: ["permissions-catalog"],
    queryFn: async () => {
      const res = await api.get<Permission[]>("/v1/access/permissions")
      return res.data
    },
    enabled: canAccess(myPerms, "system.roles.manage"),
  })

  const { data: roles = [] } = useQuery({
    queryKey: ["roles"],
    queryFn: async () => {
      const res = await api.get<Role[]>("/v1/access/roles")
      return res.data
    },
    enabled: canAccess(myPerms, "system.roles.manage"),
  })

  const { data: myRoleAssignments = [] } = useQuery({
    queryKey: ["access", "me", "roles"],
    queryFn: async () => {
      const res = await api.get<{ role_id: number }[]>("/v1/access/me/roles")
      return res.data
    },
    enabled: canAccess(myPerms, "system.roles.manage"),
  })

  const myRoleIds = new Set(myRoleAssignments.map((a) => a.role_id))
  const selectedRole = roles.find((r) => r.id === selectedRoleId)
  const isOwnRole = selectedRoleId != null && myRoleIds.has(selectedRoleId)

  const savePerms = useMutation({
    mutationFn: async () => {
      if (!selectedRoleId) return
      await api.put(`/v1/access/roles/${selectedRoleId}/permissions`, {
        permission_codes: draftCodes,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles"] })
    },
  })

  function selectRole(role: Role) {
    setSelectedRoleId(role.id)
    setDraftCodes([...role.permission_codes])
  }

  function toggleCode(code: string) {
    setDraftCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code],
    )
  }

  const byModule = allPermissions.reduce<Record<string, Permission[]>>((acc, p) => {
    ;(acc[p.module] ??= []).push(p)
    return acc
  }, {})

  return (
    <div className="flex gap-6 p-6">
      <div className="w-56 shrink-0 space-y-2">
        <h1 className="text-lg font-semibold">Roles</h1>
        <ul className="space-y-1">
          {roles.map((role) => (
            <li key={role.id}>
              <button
                type="button"
                className={`w-full rounded-md px-2 py-1.5 text-left text-sm ${
                  selectedRoleId === role.id ? "bg-muted font-medium" : "hover:bg-muted/60"
                }`}
                onClick={() => selectRole(role)}
              >
                {role.name}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="min-w-0 flex-1">
        {selectedRole ? (
          <>
            <h2 className="mb-4 text-base font-semibold">{selectedRole.name} permissions</h2>
            <p className="mb-4 text-sm text-muted-foreground">
              You can only grant permissions you already hold. You cannot change permissions for a
              role assigned to you — another authorized user must do that.
            </p>
            {isOwnRole ? (
              <p className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
                This role is assigned to your account. Saving is disabled so you cannot grant
                document permissions to yourself.
              </p>
            ) : null}
            {Object.entries(byModule).map(([module, perms]) => (
              <div key={module} className="mb-4">
                <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                  {module}
                </p>
                <ul className="grid gap-1 sm:grid-cols-2">
                  {perms.map((p) => {
                    const grantable = canAccess(myPerms, p.code)
                    return (
                      <li key={p.code} className="flex items-center gap-2 text-sm">
                        <input
                          id={p.code}
                          type="checkbox"
                          checked={draftCodes.includes(p.code)}
                          disabled={!grantable || selectedRole.is_system || isOwnRole}
                          onChange={() => toggleCode(p.code)}
                        />
                        <label htmlFor={p.code} className={!grantable ? "opacity-50" : ""}>
                          {p.name}
                        </label>
                      </li>
                    )
                  })}
                </ul>
              </div>
            ))}
            <Button
              onClick={() => savePerms.mutate()}
              disabled={savePerms.isPending || selectedRole.is_system || isOwnRole}
            >
              Save permissions
            </Button>
            {savePerms.isError && (
              <p className="mt-2 text-sm text-destructive">
                {(savePerms.error as { response?: { data?: { detail?: string } } })?.response
                  ?.data?.detail ?? "Failed to save"}
              </p>
            )}
          </>
        ) : (
          <p className="text-sm text-muted-foreground">Select a role to edit permissions.</p>
        )}
      </div>
    </div>
  )
}
