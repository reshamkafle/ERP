import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Navigate, Route, Routes } from "react-router-dom"

import { AppLayout } from "@/components/AppLayout"
import { RequireAuth } from "@/components/RequireAuth"
import { AuthProvider, useAuth } from "@/context/AuthContext"
import { DashboardPage } from "@/pages/DashboardPage"
import { ReportsPage } from "@/pages/ReportsPage"
import { CustomerDetailPage } from "@/pages/CustomerDetailPage"
import { CustomersPage } from "@/pages/CustomersPage"
import { InventoryPage } from "@/pages/InventoryPage"
import { PurchasesPage } from "@/pages/PurchasesPage"
import { SupplierDetailPage } from "@/pages/SupplierDetailPage"
import { SuppliersPage } from "@/pages/SuppliersPage"
import { LoginPage } from "@/pages/LoginPage"
import { PosPage } from "@/pages/PosPage"
import { SaleDetailPage } from "@/pages/SaleDetailPage"
import { SalesPage } from "@/pages/SalesPage"

const queryClient = new QueryClient()

function HomeRedirect() {
  const { user } = useAuth()
  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }
  return <Navigate to="/dashboard" replace />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<RequireAuth />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<HomeRedirect />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/customers" element={<CustomersPage />} />
              <Route path="/customers/:id" element={<CustomerDetailPage />} />
              <Route path="/suppliers" element={<SuppliersPage />} />
              <Route path="/suppliers/:id" element={<SupplierDetailPage />} />
              <Route path="/purchases" element={<PurchasesPage />} />
              <Route path="/sales" element={<SalesPage />} />
              <Route path="/sales/:id" element={<SaleDetailPage />} />
              <Route path="/pos" element={<PosPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
