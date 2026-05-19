"""Fake ChatOpenAI for agent graph tests without a real LLM server."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


class FakeStructuredRunnable:
    def __init__(
        self,
        schema: type[BaseModel],
        handler: Callable[[list[Any]], BaseModel],
        *,
        raise_on_invoke: bool = False,
    ) -> None:
        self._schema = schema
        self._handler = handler
        self._raise_on_invoke = raise_on_invoke

    async def ainvoke(self, messages: list[Any]) -> BaseModel:
        if self._raise_on_invoke:
            raise RuntimeError("simulated LLM failure")
        return self._handler(messages)


class FakeLLM:
    """Minimal stand-in for ChatOpenAI.with_structured_output(...).ainvoke."""

    def __init__(
        self,
        handlers: dict[type[BaseModel], Callable[[list[Any]], BaseModel]],
        *,
        raise_schemas: set[type[BaseModel]] | None = None,
    ) -> None:
        self._handlers = handlers
        self._raise_schemas = raise_schemas or set()

    def with_structured_output(self, schema: type[BaseModel]) -> FakeStructuredRunnable:
        handler = self._handlers.get(schema)
        if handler is None:
            raise KeyError(f"No fake handler registered for {schema.__name__}")
        return FakeStructuredRunnable(
            schema,
            handler,
            raise_on_invoke=schema in self._raise_schemas,
        )


def _message_text(messages: list[Any]) -> str:
    parts: list[str] = []
    for msg in messages:
        content = getattr(msg, "content", msg)
        parts.append(str(content))
    return "\n".join(parts)


def build_procurement_fake_llm() -> FakeLLM:
    from app.agents.procurement_graph import LineSuggestion, SpecialistLines, SupervisorResult

    def specialist_handler(messages: list[Any]) -> SpecialistLines:
        text = _message_text(messages)
        if "Below-threshold" in text:
            return SpecialistLines(
                lines=[LineSuggestion(product_id=1, suggested_qty=8, rationale="mock threshold")],
            )
        if "Velocity" in text:
            return SpecialistLines(
                lines=[LineSuggestion(product_id=2, suggested_qty=20, rationale="mock velocity")],
            )
        if "Promotion-boost" in text or "promotional" in text.lower():
            return SpecialistLines(
                lines=[LineSuggestion(product_id=3, suggested_qty=12, rationale="mock promotion")],
            )
        return SpecialistLines(lines=[])

    def supervisor_handler(_messages: list[Any]) -> SupervisorResult:
        return SupervisorResult(
            lines=[
                LineSuggestion(product_id=1, suggested_qty=8, rationale="mock merge 1"),
                LineSuggestion(product_id=2, suggested_qty=20, rationale="mock merge 2"),
            ],
            merge_notes="Mock LLM supervisor merge",
        )

    return FakeLLM(
        {
            SpecialistLines: specialist_handler,
            SupervisorResult: supervisor_handler,
        },
    )


def build_procurement_failing_llm() -> FakeLLM:
    from app.agents.procurement_graph import SpecialistLines, SupervisorResult

    llm = build_procurement_fake_llm()
    llm._raise_schemas = {SupervisorResult}
    return llm


def build_promotion_fake_llm() -> FakeLLM:
    from app.agents.promotion_graph import (
        PricingLineOut,
        PricingProjectOut,
        PricingSpecialistResult,
        RelatedItemOut,
        RelationProjectOut,
        RelationSpecialistResult,
        SupervisorProjectOut,
        SupervisorResult,
    )

    def relations_handler(_messages: list[Any]) -> RelationSpecialistResult:
        return RelationSpecialistResult(
            projects=[
                RelationProjectOut(
                    project_id="mock-p1",
                    anchor_product_id=1,
                    related_items=[
                        RelatedItemOut(
                            product_id=2,
                            sku="DEMO-REL-A1",
                            name="Related Alpha",
                            relationship_note="mock pair",
                        ),
                    ],
                    rationale="Mock relations project 1",
                    confidence="high",
                ),
                RelationProjectOut(
                    project_id="mock-p2",
                    anchor_product_id=4,
                    related_items=[
                        RelatedItemOut(
                            product_id=5,
                            sku="DEMO-REL-B1",
                            name="Related Beta",
                            relationship_note="mock pair 2",
                        ),
                    ],
                    rationale="Mock relations project 2",
                    confidence="medium",
                ),
            ],
        )

    def pricing_handler(_messages: list[Any]) -> PricingSpecialistResult:
        return PricingSpecialistResult(
            projects=[
                PricingProjectOut(
                    project_id="mock-p1",
                    anchor_product_id=1,
                    lines=[
                        PricingLineOut(
                            product_id=2,
                            sku="DEMO-REL-A1",
                            name="Related Alpha",
                            discount_kind="percent",
                            discount_percent=12.0,
                            duration_days=21,
                            rationale="mock pricing",
                        ),
                    ],
                    confidence="high",
                ),
                PricingProjectOut(
                    project_id="mock-p2",
                    anchor_product_id=4,
                    lines=[
                        PricingLineOut(
                            product_id=5,
                            sku="DEMO-REL-B1",
                            name="Related Beta",
                            discount_kind="percent",
                            discount_percent=8.0,
                            duration_days=14,
                            rationale="mock pricing 2",
                        ),
                    ],
                    confidence="medium",
                ),
            ],
        )

    def supervisor_handler(_messages: list[Any]) -> SupervisorResult:
        return SupervisorResult(
            projects=[
                SupervisorProjectOut(
                    project_id="mock-p1",
                    anchor={"product_id": 1, "sku": "DEMO-ANCHOR-A", "name": "Anchor Alpha"},
                    related_items=[
                        {
                            "product_id": 2,
                            "sku": "DEMO-REL-A1",
                            "name": "Related Alpha",
                            "discount_kind": "percent",
                            "discount_percent": 12.0,
                            "duration_days": 21,
                            "rationale": "mock supervisor",
                            "confidence": "high",
                        },
                    ],
                    rationale="Mock supervisor bundle 1",
                    confidence="high",
                ),
            ],
            merge_notes="Mock promotion supervisor",
        )

    return FakeLLM(
        {
            RelationSpecialistResult: relations_handler,
            PricingSpecialistResult: pricing_handler,
            SupervisorResult: supervisor_handler,
        },
    )


def build_promotion_failing_llm() -> FakeLLM:
    from app.agents.promotion_graph import SupervisorResult

    llm = build_promotion_fake_llm()
    llm._raise_schemas = {SupervisorResult}
    return llm
