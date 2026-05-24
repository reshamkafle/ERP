"""Create ERP documents via API (Documents UI removed)."""

from __future__ import annotations

import httpx


def create_erp_document(
    api_client: httpx.Client,
    *,
    document_type: str,
    title: str,
    reference_number: str,
) -> dict:
    res = api_client.post(
        "/api/v1/erp-documents",
        json={
            "document_type": document_type,
            "title": title,
            "reference_number": reference_number,
            "content": {},
        },
    )
    res.raise_for_status()
    return res.json()
