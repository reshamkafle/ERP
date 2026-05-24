"""ERP document journey CRUD tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import erp_document as erp_document_crud
from app.documents.journey import JOURNEY_STEPS
from app.models.enums import ErpDocumentType
from app.schemas.erp_document import ErpDocumentCreate


@pytest.mark.asyncio
async def test_journey_has_23_steps() -> None:
    assert len(JOURNEY_STEPS) == 23
    assert JOURNEY_STEPS[0].document_type == ErpDocumentType.TECH_PACK
    assert JOURNEY_STEPS[-1].document_type == ErpDocumentType.LANDED_COST


@pytest.mark.asyncio
async def test_create_list_delete_document(db_session: AsyncSession) -> None:
    created = await erp_document_crud.create_erp_document(
        db_session,
        ErpDocumentCreate(
            document_type=ErpDocumentType.GRN,
            title="GRN for shipment A",
            reference_number="SHIP-A",
        ),
    )
    assert created.journey_step == 4
    assert created.phase == "Inbound & quality"
    assert created.document_number.startswith("GRN-")

    items, total = await erp_document_crud.list_erp_documents(
        db_session,
        document_type=ErpDocumentType.GRN,
    )
    assert total >= 1
    assert any(d.id == created.id for d in items)

    read = erp_document_crud.document_to_read(created)
    assert read.type_label == "Goods Received Note (GRN)"

    await erp_document_crud.delete_erp_document(db_session, created)
