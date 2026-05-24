import { QueryClientProvider } from "@tanstack/react-query"
import { Navigate, Route, Routes } from "react-router-dom"

import { AppLayout } from "@/components/AppLayout"
import { RequireAuth } from "@/components/RequireAuth"
import { RequirePermission } from "@/components/RequirePermission"
import { AuthProvider, useAuth } from "@/context/AuthContext"
import { AccessControlPage } from "@/pages/AccessControlPage"
import { UsersManagementPage } from "@/pages/UsersManagementPage"
import { BomPage } from "@/pages/BomPage"
import { CustomerDetailPage } from "@/pages/CustomerDetailPage"
import { CustomersPage } from "@/pages/CustomersPage"
import { DashboardPage } from "@/pages/DashboardPage"
import { ForbiddenPage } from "@/pages/ForbiddenPage"
import { FabricRollsPage } from "@/pages/FabricRollsPage"
import { InventoryPage } from "@/pages/InventoryPage"
import { ProductVariantMatrixPage } from "@/pages/ProductVariantMatrixPage"
import { LocationsPage } from "@/pages/LocationsPage"
import { WarehousesPage } from "@/pages/WarehousesPage"
import { LoginPage } from "@/pages/LoginPage"
import { PosPage } from "@/pages/PosPage"
import { PromotionsPage } from "@/pages/PromotionsPage"
import { PurchasesPage } from "@/pages/PurchasesPage"
import { ReportsPage } from "@/pages/ReportsPage"
import { SaleDetailPage } from "@/pages/SaleDetailPage"
import { SalesPage } from "@/pages/SalesPage"
import { SettingsLayoutPage } from "@/pages/SettingsLayoutPage"
import { SettingsProfilePage } from "@/pages/SettingsProfilePage"
import { SupplierDetailPage } from "@/pages/SupplierDetailPage"
import { SuppliersPage } from "@/pages/SuppliersPage"
import { ErpModulesIndexPage } from "@/pages/ErpModulesIndexPage"
import { FinanceModulePage } from "@/pages/FinanceModulePage"
import { HcmModulePage } from "@/pages/HcmModulePage"
import { ManufacturingModulePage } from "@/pages/ManufacturingModulePage"
import { ProductionOrderDetailPage } from "@/pages/ProductionOrderDetailPage"
import { ProductionPlanningPage } from "@/pages/ProductionPlanningPage"
import { CrmModulePage } from "@/pages/CrmModulePage"
import { ProjectsModulePage } from "@/pages/ProjectsModulePage"
import { PlatformModulePage } from "@/pages/PlatformModulePage"
import { ModuleHubPage } from "@/pages/ModuleHubPage"
import { ProcurementModulePage } from "@/pages/ProcurementModulePage"
import { ScmModulePage } from "@/pages/ScmModulePage"
import { TmsModulePage } from "@/pages/TmsModulePage"
import { canAccess, canAccessAny } from "@/lib/permissions"
import { queryClient } from "@/lib/query-client"

const MODULE_ROUTES: { path: string; permission: string }[] = [
  { path: "/warehouse", permission: "warehouse.ops.read" },
  { path: "/sales-distribution", permission: "sales.dist.read" },
]

function HomeRedirect() {
  const { permissions, isBootstrapping } = useAuth()
  if (isBootstrapping) return null
  if (canAccess(permissions, "reports.dashboard.read")) {
    return <Navigate to="/dashboard" replace />
  }
  if (canAccess(permissions, "sales.pos.use")) {
    return <Navigate to="/pos" replace />
  }
  if (canAccessAny(permissions, ["sales.orders.read"])) {
    return <Navigate to="/sales" replace />
  }
  return <Navigate to="/settings/profile" replace />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forbidden" element={<ForbiddenPage />} />
          <Route element={<RequireAuth />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<HomeRedirect />} />
              <Route
                path="/dashboard"
                element={
                  <RequirePermission permission="reports.dashboard.read">
                    <DashboardPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/modules"
                element={
                  <RequirePermission permission="reports.dashboard.read">
                    <ErpModulesIndexPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/finance"
                element={
                  <RequirePermission permission="finance.records.read">
                    <FinanceModulePage />
                  </RequirePermission>
                }
              />
              <Route
                path="/hcm"
                element={
                  <RequirePermission permission="hcm.records.read">
                    <HcmModulePage />
                  </RequirePermission>
                }
              />
              <Route
                path="/procurement"
                element={
                  <RequirePermission permission="procurement.records.read">
                    <ProcurementModulePage />
                  </RequirePermission>
                }
              />
              <Route
                path="/scm"
                element={
                  <RequirePermission permission="scm.records.read">
                    <ScmModulePage />
                  </RequirePermission>
                }
              />
              <Route
                path="/tms"
                element={
                  <RequirePermission permission="tms.records.read">
                    <TmsModulePage />
                  </RequirePermission>
                }
              />
              <Route
                path="/manufacturing"
                element={
                  <RequirePermission permission="manufacturing.ops.read">
                    <ManufacturingModulePage />
                  </RequirePermission>
                }
              />
              <Route
                path="/manufacturing/planning"
                element={
                  <RequirePermission permission="manufacturing.planning.read">
                    <ProductionPlanningPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/manufacturing/orders/:id"
                element={
                  <RequirePermission permission="manufacturing.ops.read">
                    <ProductionOrderDetailPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/crm"
                element={
                  <RequirePermission permission="crm.records.read">
                    <CrmModulePage />
                  </RequirePermission>
                }
              />
              <Route
                path="/projects"
                element={
                  <RequirePermission permission="projects.records.read">
                    <ProjectsModulePage />
                  </RequirePermission>
                }
              />
              <Route
                path="/platform"
                element={
                  <RequirePermission permission="platform.records.read">
                    <PlatformModulePage />
                  </RequirePermission>
                }
              />
              {MODULE_ROUTES.map(({ path, permission }) => (
                <Route
                  key={path}
                  path={path}
                  element={
                    <RequirePermission permission={permission}>
                      <ModuleHubPage routePath={path} />
                    </RequirePermission>
                  }
                />
              ))}
              <Route
                path="/reports"
                element={
                  <RequirePermission
                    anyOf={[
                      "reports.reports.read",
                      "reports.merchandiser.read",
                      "reports.finance.read",
                      "reports.marketing.read",
                      "reports.warehouse.read",
                      "reports.it.read",
                      "reports.manager.read",
                    ]}
                  >
                    <ReportsPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/inventory"
                element={
                  <RequirePermission permission="warehouse.inventory.read">
                    <InventoryPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/inventory/variants"
                element={
                  <RequirePermission permission="warehouse.inventory.read">
                    <ProductVariantMatrixPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/inventory/fabric-rolls"
                element={
                  <RequirePermission permission="warehouse.material_rolls.read">
                    <FabricRollsPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/warehouses"
                element={
                  <RequirePermission permission="warehouse.ops.read">
                    <WarehousesPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/locations"
                element={
                  <RequirePermission permission="warehouse.ops.read">
                    <LocationsPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/bom"
                element={
                  <RequirePermission permission="warehouse.bom.read">
                    <BomPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/customers"
                element={
                  <RequirePermission permission="sales.customers.read">
                    <CustomersPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/customers/:id"
                element={
                  <RequirePermission permission="sales.customers.write">
                    <CustomerDetailPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/suppliers"
                element={
                  <RequirePermission permission="warehouse.suppliers.read">
                    <SuppliersPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/suppliers/:id"
                element={
                  <RequirePermission permission="warehouse.suppliers.read">
                    <SupplierDetailPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/purchases"
                element={
                  <RequirePermission anyOf={["warehouse.purchases.read", "warehouse.purchases.write"]}>
                    <PurchasesPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/promotions"
                element={
                  <RequirePermission permission="sales.promotions.manage">
                    <PromotionsPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/sales"
                element={
                  <RequirePermission permission="sales.orders.read">
                    <SalesPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/sales/:id"
                element={
                  <RequirePermission permission="sales.orders.read">
                    <SaleDetailPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/pos"
                element={
                  <RequirePermission permission="sales.pos.use">
                    <PosPage />
                  </RequirePermission>
                }
              />
              <Route path="/settings/profile" element={<SettingsProfilePage />} />
              <Route
                path="/settings/layout"
                element={
                  <RequirePermission permission="profile.layout.configure">
                    <SettingsLayoutPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/settings/access"
                element={
                  <RequirePermission permission="system.roles.manage">
                    <AccessControlPage />
                  </RequirePermission>
                }
              />
              <Route
                path="/settings/users"
                element={
                  <RequirePermission anyOf={["system.users.read", "system.users.manage"]}>
                    <UsersManagementPage />
                  </RequirePermission>
                }
              />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
