from typing import Literal

from pydantic import BaseModel, Field

SearchEntityType = Literal[
    "customer",
    "sale",
    "erp_document",
    "purchase",
    "production_order",
    "supplier",
    "product",
    "material_roll",
    "warehouse",
    "storage_location",
    "module_record",
    "crm_lead",
    "crm_opportunity",
    "crm_contact",
]

SearchGroup = Literal["pages", "sales", "procurement", "manufacturing", "inventory", "modules", "crm"]


class SearchRelatedHit(BaseModel):
    entity_type: SearchEntityType
    entity_id: int
    title: str
    route: str


class SearchHit(BaseModel):
    entity_type: SearchEntityType
    entity_id: int
    title: str
    subtitle: str | None = None
    route: str
    group: SearchGroup
    highlights: list[str] = Field(default_factory=list)
    related: list[SearchRelatedHit] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchHit]
