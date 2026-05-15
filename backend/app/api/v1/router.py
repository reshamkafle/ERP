from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    customers,
    dashboard,
    health,
    inventory,
    purchases,
    reports,
    sales,
    suppliers,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(inventory.router, tags=["inventory"])
api_router.include_router(customers.router, tags=["customers"])
api_router.include_router(suppliers.router, tags=["suppliers"])
api_router.include_router(purchases.router, tags=["purchases"])
api_router.include_router(sales.router, tags=["sales"])
