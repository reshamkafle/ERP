from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import module_record as module_record_crud
from app.dependencies.auth import get_current_user, get_current_user_permissions
from app.models.user import User
from app.modules.catalog import MODULE_BY_CODE, MODULE_CATALOG
from app.schemas.module_record import (
    ModuleCatalogResponse,
    ModuleDefRead,
    ModuleFeatureDefRead,
    ModuleOverviewResponse,
    ModuleRecordCreate,
    ModuleRecordListResponse,
    ModuleRecordRead,
    ModuleRecordUpdate,
)
from app.services.module_overview import build_module_overview

router = APIRouter(prefix="/erp-modules")


def _get_module_or_404(module_code: str):
    module = MODULE_BY_CODE.get(module_code)
    if module is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Unknown module")
    return module


def _assert_read(module_code: str, perms: set[str]) -> None:
    module = _get_module_or_404(module_code)
    if module.permission_read not in perms:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def _assert_write(module_code: str, perms: set[str]) -> None:
    module = _get_module_or_404(module_code)
    if module.permission_write not in perms:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.get("/catalog", response_model=ModuleCatalogResponse)
async def get_module_catalog(
    perms: Annotated[set[str], Depends(get_current_user_permissions)],
    _: Annotated[User, Depends(get_current_user)],
) -> ModuleCatalogResponse:
    modules = [
        ModuleDefRead(
            code=m.code,
            name=m.name,
            short_name=m.short_name,
            description=m.description,
            route_path=m.route_path,
            permission_read=m.permission_read,
            permission_write=m.permission_write,
            linked_routes=list(m.linked_routes),
            features=[
                ModuleFeatureDefRead(code=f.code, name=f.name, description=f.description)
                for f in m.features
            ],
        )
        for m in MODULE_CATALOG
        if m.permission_read in perms
    ]
    return ModuleCatalogResponse(modules=modules)


@router.get("/{module_code}/overview", response_model=ModuleOverviewResponse)
async def get_module_overview(
    module_code: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    perms: Annotated[set[str], Depends(get_current_user_permissions)],
    _: Annotated[User, Depends(get_current_user)],
) -> ModuleOverviewResponse:
    _assert_read(module_code, perms)
    overview = await build_module_overview(db, module_code)
    if overview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Module not found")
    return overview


@router.get("/{module_code}/records", response_model=ModuleRecordListResponse)
async def list_records(
    module_code: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    perms: Annotated[set[str], Depends(get_current_user_permissions)],
    _: Annotated[User, Depends(get_current_user)],
    feature_code: str | None = None,
    search: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> ModuleRecordListResponse:
    _assert_read(module_code, perms)
    items, total = await module_record_crud.list_module_records(
        db,
        module_code=module_code,
        feature_code=feature_code,
        search=search,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return ModuleRecordListResponse(
        items=[ModuleRecordRead.model_validate(r) for r in items],
        total=total,
    )


@router.get("/{module_code}/records/{record_id}", response_model=ModuleRecordRead)
async def get_record(
    module_code: str,
    record_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    perms: Annotated[set[str], Depends(get_current_user_permissions)],
    _: Annotated[User, Depends(get_current_user)],
) -> ModuleRecordRead:
    _assert_read(module_code, perms)
    record = await module_record_crud.get_module_record(db, record_id)
    if record is None or record.module_code != module_code:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    return ModuleRecordRead.model_validate(record)


@router.post(
    "/{module_code}/records",
    response_model=ModuleRecordRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_record(
    module_code: str,
    body: ModuleRecordCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    perms: Annotated[set[str], Depends(get_current_user_permissions)],
    _: Annotated[User, Depends(get_current_user)],
) -> ModuleRecordRead:
    module = _get_module_or_404(module_code)
    _assert_write(module_code, perms)
    valid_features = {f.code for f in module.features}
    if body.feature_code not in valid_features:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid feature_code")
    if module_code == "manufacturing" and body.feature_code == "production_orders":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Production orders use POST /api/v1/manufacturing/production-orders",
        )
    record = await module_record_crud.create_module_record(db, module_code, body)
    return ModuleRecordRead.model_validate(record)


@router.patch("/{module_code}/records/{record_id}", response_model=ModuleRecordRead)
async def update_record(
    module_code: str,
    record_id: int,
    body: ModuleRecordUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    perms: Annotated[set[str], Depends(get_current_user_permissions)],
    _: Annotated[User, Depends(get_current_user)],
) -> ModuleRecordRead:
    _assert_write(module_code, perms)
    record = await module_record_crud.get_module_record(db, record_id)
    if record is None or record.module_code != module_code:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    if module_code == "manufacturing" and record.feature_code == "production_orders":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Production orders use PATCH /api/v1/manufacturing/production-orders/{id}",
        )
    record = await module_record_crud.update_module_record(db, record, body)
    return ModuleRecordRead.model_validate(record)


@router.delete("/{module_code}/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    module_code: str,
    record_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    perms: Annotated[set[str], Depends(get_current_user_permissions)],
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    _assert_write(module_code, perms)
    record = await module_record_crud.get_module_record(db, record_id)
    if record is None or record.module_code != module_code:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Record not found")
    await module_record_crud.delete_module_record(db, record)
