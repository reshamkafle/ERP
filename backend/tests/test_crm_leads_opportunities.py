from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crm as crm_crud
from app.crud import customer as customer_crud
from app.models.enums import LeadStatus, OpportunityStage
from app.schemas.crm import CrmLeadCreate, CrmOpportunityCreate
from app.schemas.customer import CustomerCreate


@pytest.mark.asyncio
async def test_lead_and_opportunity_crud(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()

    customer = await customer_crud.create_customer(
        db_session,
        CustomerCreate(name="CRM Test Co", email="crmtest@example.com"),
    )

    lead = await crm_crud.create_lead(
        db_session,
        CrmLeadCreate(company_name="Prospect Inc", source="web", status=LeadStatus.NEW),
    )
    assert lead.id is not None

    opp = await crm_crud.create_opportunity(
        db_session,
        CrmOpportunityCreate(
            customer_id=customer.id,
            lead_id=lead.id,
            title="Enterprise deal",
            stage=OpportunityStage.QUALIFICATION,
            probability=40,
            expected_value=Decimal("25000"),
        ),
    )
    assert opp.customer_id == customer.id
    assert opp.lead_id == lead.id

    items, total = await crm_crud.list_opportunities(db_session, customer_id=customer.id)
    assert total >= 1
    assert any(o.id == opp.id for o in items)

    stage_rows, pipeline_total = await crm_crud.pipeline_summary(db_session)
    assert pipeline_total >= Decimal("0")

    from app.schemas.crm import CrmLeadUpdate, CrmOpportunityUpdate

    updated_lead = await crm_crud.update_lead(
        db_session,
        lead,
        CrmLeadUpdate(
            lead_score=75,
            bant_budget="100k",
            bant_authority="CFO",
            bant_need="ERP",
            bant_timeline="Q3",
        ),
    )
    assert updated_lead.lead_score == 75
    assert updated_lead.bant_budget == "100k"

    updated_opp = await crm_crud.update_opportunity(
        db_session,
        opp,
        CrmOpportunityUpdate(stage=OpportunityStage.PROPOSAL, competitor_info="Rival Co"),
    )
    assert updated_opp.stage == OpportunityStage.PROPOSAL
    assert updated_opp.competitor_info == "Rival Co"
    history = await crm_crud.list_opportunity_stage_history(db_session, opp.id)
    assert len(history) >= 1
