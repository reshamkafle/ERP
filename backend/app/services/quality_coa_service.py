"""Quality inspection results and Certificate of Analysis document generation."""

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ErpDocumentStatus, ErpDocumentType
from app.models.erp_document import ErpDocument
from app.models.manufacturing_ops import (
    InspectionCharacteristic,
    InspectionResult,
    NonConformance,
    QualityInspectionPlan,
)
from app.schemas.manufacturing import InspectionResultIn, NonConformanceCreate


async def record_inspection_result(
    db: AsyncSession,
    payload: InspectionResultIn,
    user_id: int | None,
) -> InspectionResult:
    char = await db.get(InspectionCharacteristic, payload.characteristic_id)
    if char is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Characteristic not found")

    passed = True
    if char.attribute_type == "NUMERIC" and payload.measured_value is not None:
        if char.min_value is not None and payload.measured_value < char.min_value:
            passed = False
        if char.max_value is not None and payload.measured_value > char.max_value:
            passed = False

    result = InspectionResult(
        plan_id=payload.plan_id,
        production_order_id=payload.production_order_id,
        characteristic_id=payload.characteristic_id,
        measured_value=payload.measured_value,
        attribute_result=payload.attribute_result,
        passed=passed,
        inspected_by_id=user_id,
    )
    db.add(result)
    await db.flush()
    await db.refresh(result)
    return result


async def create_non_conformance(
    db: AsyncSession, payload: NonConformanceCreate
) -> NonConformance:
    from sqlalchemy import func

    count = (
        await db.execute(select(func.count()).select_from(NonConformance)),
    ).scalar_one() or 0
    ref = f"NCR-{count + 1:06d}"
    ncr = NonConformance(reference=ref, **payload.model_dump())
    db.add(ncr)
    await db.flush()
    await db.refresh(ncr)
    return ncr


async def generate_coa_document(
    db: AsyncSession,
    *,
    plan_id: int,
    production_order_id: int | None,
    user_id: int | None,
) -> ErpDocument:
    plan = await db.get(QualityInspectionPlan, plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Inspection plan not found")

    result = await db.execute(
        select(InspectionResult)
        .where(InspectionResult.plan_id == plan_id)
        .where(InspectionResult.passed.is_(True)),
    )
    passed_results = list(result.scalars().all())
    if not passed_results:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="No passed inspection results for COA",
        )

    content = {
        "plan_code": plan.code,
        "plan_name": plan.name,
        "stage": plan.stage.value,
        "production_order_id": production_order_id,
        "results_count": len(passed_results),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    doc = ErpDocument(
        document_type=ErpDocumentType.CERTIFICATE_OF_ANALYSIS,
        title=f"COA — {plan.name}",
        status=ErpDocumentStatus.ISSUED,
        reference_number=f"COA-{plan.code}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        content=content,
        created_by_id=user_id,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc
