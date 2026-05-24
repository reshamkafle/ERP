from fastapi import APIRouter

from app.api.v1.endpoints import (
    access_control,
    auth,
    bom,
    chart_of_accounts,
    crm,
    customers,
    dashboard,
    erp_documents,
    health,
    inventory,
    inventory_variants,
    material_rolls,
    payment_methods,
    payments,
    preferences,
    procurement,
    erp_modules,
    garment_planning,
    manufacturing,
    promotion_runs,
    purchases,
    reports,
    search,
    sales,
    suppliers,
    tax_rates,
    warehouses,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(access_control.router, tags=["access-control"])
api_router.include_router(preferences.router, tags=["preferences"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(inventory_variants.router, tags=["inventory-variants"])
api_router.include_router(inventory.router, tags=["inventory"])
api_router.include_router(material_rolls.router, tags=["material-rolls"])
api_router.include_router(warehouses.router, tags=["warehouses"])
api_router.include_router(warehouses.locations_router, tags=["storage-locations"])
api_router.include_router(bom.router, tags=["bom"])
api_router.include_router(customers.router, tags=["customers"])
api_router.include_router(crm.router, tags=["crm"])
api_router.include_router(suppliers.router, tags=["suppliers"])
api_router.include_router(erp_documents.router, tags=["erp-documents"])
api_router.include_router(procurement.router, tags=["procurement"])
api_router.include_router(promotion_runs.router, tags=["promotions"])
api_router.include_router(purchases.router, tags=["purchases"])
api_router.include_router(sales.router, tags=["sales"])
api_router.include_router(erp_modules.router, tags=["erp-modules"])
api_router.include_router(manufacturing.router, tags=["manufacturing"])
api_router.include_router(garment_planning.router, tags=["garment-planning"])
api_router.include_router(tax_rates.router, tags=["tax-rates"])
api_router.include_router(payment_methods.router, tags=["payment-methods"])
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(chart_of_accounts.router, tags=["chart-of-accounts"])
