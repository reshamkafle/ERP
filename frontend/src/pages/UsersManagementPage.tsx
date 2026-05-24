import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo, useState } from "react"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { api } from "@/lib/api"
import { useAuth } from "@/context/AuthContext"
import { canAccess } from "@/lib/permissions"

type UserRole = {
  role_id: number
  role_name: string
  role_type: string
  department: string | null
}

type SystemUser = {
  id: number
  email: string
  legacy_role: string
  is_active: boolean
  roles: UserRole[]
  permission_codes: string[]
}

type RoleOption = {
  id: number
  name: string
  role_type: string
  permission_codes: string[]
}

type Permission = { id: number; code: string; name: string; module: string }

export function UsersManagementPage() {
  const { user: currentUser, permissions: myPerms } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
  const [roleToAssign, setRoleToAssign] = useState("")
  const [draftCodes, setDraftCodes] = useState<string[]>([])

  const canManage = canAccess(myPerms, "system.users.manage")

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["access", "users"],
    queryFn: async () => {
      const res = await api.get<SystemUser[]>("/v1/access/users")
      return res.data
    },
  })

  const { data: allPermissions = [] } = useQuery({
    queryKey: ["permissions-catalog"],
    queryFn: async () => {
      const res = await api.get<Permission[]>("/v1/access/permissions")
      return res.data
    },
    enabled: canManage || canAccess(myPerms, "system.users.read"),
  })

  const { data: roles = [] } = useQuery({
    queryKey: ["roles"],
    queryFn: async () => {
      const res = await api.get<RoleOption[]>("/v1/access/roles")
      return res.data
    },
    enabled: canManage,
  })

  const filteredUsers = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return users
    return users.filter(
      (u) =>
        u.email.toLowerCase().includes(q) ||
        u.legacy_role.toLowerCase().includes(q) ||
        u.roles.some((r) => r.role_name.toLowerCase().includes(q)),
    )
  }, [search, users])

  const selectedUser = users.find((u) => u.id === selectedUserId) ?? null
  const isSelf = selectedUser != null && currentUser?.id === selectedUser.id

  useEffect(() => {
    if (selectedUser) {
      setDraftCodes([...selectedUser.permission_codes])
    } else {
      setDraftCodes([])
    }
  }, [selectedUser])

  const permissionsByModule = useMemo(() => {
    return allPermissions.reduce<Record<string, Permission[]>>((acc, p) => {
      ;(acc[p.module] ??= []).push(p)
      return acc
    }, {})
  }, [allPermissions])

  const assignableRoles = useMemo(() => {
    if (!selectedUser || !canManage) return []
    const assigned = new Set(selectedUser.roles.map((r) => r.role_id))
    return roles.filter((role) => {
      if (assigned.has(role.id)) return false
      return role.permission_codes.every((code) => canAccess(myPerms, code))
    })
  }, [canManage, myPerms, roles, selectedUser])

  const permissionsDirty = useMemo(() => {
    if (!selectedUser) return false
    const saved = [...selectedUser.permission_codes].sort().join("\0")
    const draft = [...draftCodes].sort().join("\0")
    return saved !== draft
  }, [draftCodes, selectedUser])

  const invalidateUsers = () => {
    void queryClient.invalidateQueries({ queryKey: ["access", "users"] })
  }

  const assignRole = useMutation({
    mutationFn: async ({ userId, roleId }: { userId: number; roleId: number }) => {
      await api.post(`/v1/access/users/${userId}/roles`, { role_id: roleId })
    },
    onSuccess: () => {
      invalidateUsers()
      setRoleToAssign("")
    },
  })

  const removeRole = useMutation({
    mutationFn: async ({ userId, roleId }: { userId: number; roleId: number }) => {
      await api.delete(`/v1/access/users/${userId}/roles/${roleId}`)
    },
    onSuccess: invalidateUsers,
  })

  const savePermissions = useMutation({
    mutationFn: async () => {
      if (!selectedUser) return
      await api.put(`/v1/access/users/${selectedUser.id}/permissions`, {
        permission_codes: draftCodes,
      })
    },
    onSuccess: () => {
      invalidateUsers()
    },
  })

  function togglePermission(code: string) {
    setDraftCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code],
    )
  }

  const mutationError =
    (assignRole.error as { response?: { data?: { detail?: string } } })?.response?.data
      ?.detail ??
    (removeRole.error as { response?: { data?: { detail?: string } } })?.response?.data
      ?.detail ??
    (savePermissions.error as { response?: { data?: { detail?: string } } })?.response?.data
      ?.detail

  return (
    <div className="space-y-4">
      <PageHeader
        title="Users"
        description="View every account, its assigned roles, and effective permissions. Toggle permissions per user or assign roles when you hold Manage users."
      />

      <ControlPanel>
        <Input
          className="max-w-md"
          placeholder="Search by email, legacy role, or assigned role…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      <div className="flex flex-col gap-6 xl:flex-row">
        <ContentSheet className="min-w-0 flex-1 p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Legacy role</th>
                  <th className="px-4 py-3 font-medium">Assigned roles</th>
                  <th className="px-4 py-3 font-medium">Permissions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                      Loading users…
                    </td>
                  </tr>
                ) : filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                      No users match your search.
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map((user) => (
                    <tr
                      key={user.id}
                      className={`cursor-pointer border-b border-border/60 hover:bg-muted/40 ${
                        selectedUserId === user.id ? "bg-muted/60" : ""
                      }`}
                      onClick={() => setSelectedUserId(user.id)}
                    >
                      <td className="px-4 py-3 font-medium">{user.email}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                            user.is_active
                              ? "bg-emerald-100 text-emerald-900"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {user.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{user.legacy_role}</td>
                      <td className="px-4 py-3">
                        {user.roles.length === 0 ? (
                          <span className="text-muted-foreground">None</span>
                        ) : (
                          <div className="flex flex-wrap gap-1">
                            {user.roles.map((role) => (
                              <span
                                key={role.role_id}
                                className="rounded-md bg-muted px-2 py-0.5 text-xs"
                              >
                                {role.role_name}
                              </span>
                            ))}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {user.permission_codes.length}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </ContentSheet>

        <ContentSheet className="w-full shrink-0 space-y-4 p-4 xl:w-[28rem] xl:max-h-[calc(100vh-8rem)] xl:overflow-y-auto">
          {selectedUser ? (
            <>
              <div>
                <h2 className="text-base font-semibold">{selectedUser.email}</h2>
                <p className="text-sm text-muted-foreground">
                  Legacy role: {selectedUser.legacy_role}
                </p>
              </div>

              <div>
                <h3 className="mb-2 text-sm font-semibold">Assigned roles</h3>
                {selectedUser.roles.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No dynamic roles assigned.</p>
                ) : (
                  <ul className="space-y-2">
                    {selectedUser.roles.map((role) => (
                      <li
                        key={role.role_id}
                        className="flex items-center justify-between gap-2 rounded-md border border-border px-3 py-2 text-sm"
                      >
                        <span>{role.role_name}</span>
                        {canManage ? (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            disabled={isSelf || removeRole.isPending}
                            onClick={() =>
                              removeRole.mutate({
                                userId: selectedUser.id,
                                roleId: role.role_id,
                              })
                            }
                          >
                            Remove
                          </Button>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {canManage ? (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold">Assign role</h3>
                  {isSelf ? (
                    <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
                      You cannot change your own roles. Another authorized user must do that.
                    </p>
                  ) : (
                    <div className="flex gap-2">
                      <select
                        className="h-9 min-w-0 flex-1 rounded-md border border-input bg-background px-2 text-sm"
                        value={roleToAssign}
                        onChange={(e) => setRoleToAssign(e.target.value)}
                        disabled={assignableRoles.length === 0}
                      >
                        <option value="">
                          {assignableRoles.length === 0
                            ? "No assignable roles"
                            : "Select a role…"}
                        </option>
                        {assignableRoles.map((role) => (
                          <option key={role.id} value={String(role.id)}>
                            {role.name}
                          </option>
                        ))}
                      </select>
                      <Button
                        type="button"
                        disabled={!roleToAssign || assignRole.isPending}
                        onClick={() =>
                          assignRole.mutate({
                            userId: selectedUser.id,
                            roleId: Number(roleToAssign),
                          })
                        }
                      >
                        Assign
                      </Button>
                    </div>
                  )}
                </div>
              ) : null}

              <div>
                <h3 className="mb-2 text-sm font-semibold">
                  Effective permissions ({draftCodes.length})
                </h3>
                {canManage && !isSelf ? (
                  <p className="mb-3 text-xs text-muted-foreground">
                    Check to grant, uncheck to revoke. You can only enable permissions you already
                    hold; overrides apply on top of assigned roles.
                  </p>
                ) : canManage && isSelf ? (
                  <p className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
                    You cannot change your own permissions. Another authorized user must do that.
                  </p>
                ) : (
                  <p className="mb-3 text-xs text-muted-foreground">View-only permission list.</p>
                )}

                {Object.entries(permissionsByModule).map(([module, perms]) => (
                  <div key={module} className="mb-4">
                    <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                      {module}
                    </p>
                    <ul className="grid gap-1">
                      {perms.map((p) => {
                        const grantable = canAccess(myPerms, p.code)
                        const editable = canManage && !isSelf
                        const checked = draftCodes.includes(p.code)
                        return (
                          <li key={p.code} className="flex items-center gap-2 text-sm">
                            <input
                              id={`user-perm-${selectedUser.id}-${p.code}`}
                              type="checkbox"
                              checked={checked}
                              disabled={!editable || (!grantable && !checked)}
                              onChange={() => togglePermission(p.code)}
                            />
                            <label
                              htmlFor={`user-perm-${selectedUser.id}-${p.code}`}
                              className={!grantable && editable ? "opacity-50" : ""}
                            >
                              {p.name}
                            </label>
                          </li>
                        )
                      })}
                    </ul>
                  </div>
                ))}

                {canManage && !isSelf ? (
                  <Button
                    onClick={() => savePermissions.mutate()}
                    disabled={savePermissions.isPending || !permissionsDirty}
                  >
                    Save permissions
                  </Button>
                ) : null}
              </div>

              {mutationError ? (
                <p className="text-sm text-destructive">{mutationError}</p>
              ) : null}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">
              Select a user to view roles and permissions.
            </p>
          )}
        </ContentSheet>
      </div>
    </div>
  )
}
