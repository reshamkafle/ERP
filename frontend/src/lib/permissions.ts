export function canAccess(permissions: string[], code: string): boolean {
  return permissions.includes(code)
}

export function canAccessAny(permissions: string[], codes: string[]): boolean {
  return codes.some((code) => permissions.includes(code))
}

export function canAccessAll(permissions: string[], codes: string[]): boolean {
  return codes.every((code) => permissions.includes(code))
}

/** POS-only users (e.g. cashiers) should not see back-office pages. */
export function isPosOnlyUser(permissions: string[]): boolean {
  return canAccess(permissions, "sales.pos.use") && !canAccess(permissions, "reports.dashboard.read")
}

export function canDeleteInventory(permissions: string[]): boolean {
  return canAccess(permissions, "warehouse.inventory.delete")
}

export function canDeleteCustomers(permissions: string[]): boolean {
  return canAccess(permissions, "sales.customers.delete")
}

export function canDeleteSuppliers(permissions: string[]): boolean {
  return canAccess(permissions, "warehouse.suppliers.delete")
}

export function canDeleteDocuments(permissions: string[]): boolean {
  return canAccess(permissions, "warehouse.documents.delete")
}

export function canLinkCustomers(permissions: string[]): boolean {
  return canAccess(permissions, "sales.customers.write")
}

export function canManageUsers(permissions: string[]): boolean {
  return canAccessAny(permissions, ["system.users.manage", "system.users.read"])
}
