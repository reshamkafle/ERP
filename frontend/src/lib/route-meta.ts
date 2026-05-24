/** Page titles for the Odoo-style top bar (pathname → title). */
export const ROUTE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/modules": "ERP Modules",
  "/reports": "Reports",
  "/inventory": "Inventory",
  "/bom": "Bill of materials",
  "/customers": "Customers",
  "/suppliers": "Suppliers",
  "/purchases": "Purchases",
  "/promotions": "Promotions",
  "/sales": "Sales",
  "/pos": "Point of sale",
  "/settings/profile": "Profile",
  "/settings/layout": "Layout settings",
  "/settings/access": "Access control",
  "/settings/users": "Users",
  "/forbidden": "Access denied",
}

export function titleForPath(pathname: string): string {
  if (ROUTE_TITLES[pathname]) return ROUTE_TITLES[pathname]
  if (pathname.startsWith("/customers/")) return "Customer"
  if (pathname.startsWith("/suppliers/")) return "Supplier"
  if (pathname.startsWith("/sales/")) return "Sale"
  return "ERP"
}
