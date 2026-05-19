"""Deterministic promotion signals: anchors, co-purchase affinity, category neighbors."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.enums import ItemLifecycleStatus
from app.models.product import Product
from app.models.sale import Sale, SaleItem


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class ProductSnapshot:
    product_id: int
    sku: str
    name: str
    price: Decimal
    cost_price: Decimal
    stock: int
    category_id: int | None
    product_line: str | None
    sub_category: str | None


@dataclass
class PromotionSignals:
    bundle_candidates: list[dict[str, Any]]
    warnings: list[str]


def _snap_dict(s: ProductSnapshot) -> dict[str, Any]:
    return {
        "product_id": s.product_id,
        "sku": s.sku,
        "name": s.name,
        "price": str(s.price),
        "cost_price": str(s.cost_price),
        "stock": s.stock,
        "category_id": s.category_id,
        "product_line": s.product_line,
        "sub_category": s.sub_category,
    }


async def fetch_promotion_signals(
    db: AsyncSession,
    *,
    sales_lookback_days: int,
    max_anchor_products: int,
    max_related_per_anchor: int,
    category_id: int | None = None,
    co_purchase_pair_limit: int = 800,
) -> PromotionSignals:
    """Build bundle candidates for the promotion graph (no LLM)."""
    warnings: list[str] = []
    now = _utc_now()
    start = now - timedelta(days=max(1, sales_lookback_days))

    anchor_stmt = (
        select(
            SaleItem.product_id,
            func.coalesce(func.sum(SaleItem.quantity), 0).label("qty"),
        )
        .join(Sale, Sale.id == SaleItem.sale_id)
        .join(Product, Product.id == SaleItem.product_id)
        .where(
            Sale.created_at >= start,
            Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
        )
    )
    if category_id is not None:
        anchor_stmt = anchor_stmt.where(Product.category_id == category_id)

    anchor_stmt = (
        anchor_stmt.group_by(SaleItem.product_id)
        .order_by(func.coalesce(func.sum(SaleItem.quantity), 0).desc())
        .limit(max(1, max_anchor_products))
    )
    anchor_rows = (await db.execute(anchor_stmt)).all()
    anchor_ids = [int(r.product_id) for r in anchor_rows]

    if not anchor_ids:
        warnings.append(
            "No anchor products with sales in the lookback window — using active catalog sample.",
        )
        fallback_stmt = (
            select(Product.id)
            .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE)
            .order_by(Product.id.asc())
            .limit(max(1, max_anchor_products))
        )
        if category_id is not None:
            fallback_stmt = fallback_stmt.where(Product.category_id == category_id)
        fb_rows = (await db.execute(fallback_stmt)).all()
        anchor_ids = [int(r.id) for r in fb_rows]

    if not anchor_ids:
        return PromotionSignals(bundle_candidates=[], warnings=warnings + ["No active products."])

    si1 = aliased(SaleItem)
    si2 = aliased(SaleItem)
    pair_stmt = (
        select(
            si1.product_id,
            si2.product_id,
            func.count(func.distinct(si1.sale_id)).label("cnt"),
        )
        .select_from(si1)
        .join(si2, and_(si1.sale_id == si2.sale_id, si1.product_id < si2.product_id))
        .join(Sale, Sale.id == si1.sale_id)
        .where(Sale.created_at >= start)
        .group_by(si1.product_id, si2.product_id)
        .order_by(func.count(func.distinct(si1.sale_id)).desc())
        .limit(max(1, co_purchase_pair_limit))
    )
    pair_rows = (await db.execute(pair_stmt)).all()
    co_map: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for row in pair_rows:
        p1, p2, c = int(row[0]), int(row[1]), int(row[2])
        co_map[p1].append((p2, c))
        co_map[p2].append((p1, c))

    for pid in list(co_map.keys()):
        co_map[pid].sort(key=lambda x: -x[1])
        co_map[pid] = co_map[pid][: max_related_per_anchor * 2]

    all_ids: set[int] = set(anchor_ids)
    for aid in anchor_ids:
        for rid, _ in co_map.get(aid, [])[:max_related_per_anchor]:
            all_ids.add(rid)

    snap_rows = (
        await db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                Product.price,
                Product.cost_price,
                Product.stock,
                Product.category_id,
                Product.product_line,
                Product.sub_category,
            ).where(
                Product.id.in_(all_ids),
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
            ),
        )
    ).all()
    snapshots: dict[int, ProductSnapshot] = {}
    for row in snap_rows:
        snapshots[int(row.id)] = ProductSnapshot(
            product_id=int(row.id),
            sku=row.sku,
            name=row.name,
            price=Decimal(str(row.price)),
            cost_price=Decimal(str(row.cost_price)),
            stock=int(row.stock),
            category_id=int(row.category_id) if row.category_id is not None else None,
            product_line=row.product_line,
            sub_category=row.sub_category,
        )

    bundle_candidates: list[dict[str, Any]] = []
    cap = max(1, max_related_per_anchor)

    for aid in anchor_ids:
        anchor = snapshots.get(aid)
        if anchor is None:
            continue
        related_ids: list[int] = []
        seen: set[int] = {aid}
        for rid, cnt in co_map.get(aid, [])[:cap]:
            if rid in seen or rid not in snapshots:
                continue
            seen.add(rid)
            related_ids.append(rid)

        if anchor.category_id is not None and len(related_ids) < cap:
            cat_stmt = (
                select(Product.id)
                .where(
                    Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
                    Product.category_id == anchor.category_id,
                    Product.id != aid,
                )
                .order_by(Product.id.asc())
                .limit(cap)
            )
            cat_rows = (await db.execute(cat_stmt)).scalars().all()
            for cid in cat_rows:
                cid = int(cid)
                if cid in seen or cid not in snapshots:
                    continue
                seen.add(cid)
                related_ids.append(cid)
                if len(related_ids) >= cap:
                    break

        if anchor.product_line and len(related_ids) < cap:
            seen_list = list(seen)
            pl_conditions = [
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
                Product.product_line == anchor.product_line,
                Product.id != aid,
            ]
            if seen_list:
                pl_conditions.append(~Product.id.in_(seen_list))
            pl_rows = (
                await db.execute(
                    select(
                        Product.id,
                        Product.sku,
                        Product.name,
                        Product.price,
                        Product.cost_price,
                        Product.stock,
                        Product.category_id,
                        Product.product_line,
                        Product.sub_category,
                    ).where(*pl_conditions).order_by(Product.id.asc()).limit(cap),
                )
            ).all()
            for row in pl_rows:
                pid = int(row.id)
                if pid in seen:
                    continue
                snapshots[pid] = ProductSnapshot(
                    product_id=pid,
                    sku=row.sku,
                    name=row.name,
                    price=Decimal(str(row.price)),
                    cost_price=Decimal(str(row.cost_price)),
                    stock=int(row.stock),
                    category_id=int(row.category_id) if row.category_id is not None else None,
                    product_line=row.product_line,
                    sub_category=row.sub_category,
                )
                seen.add(pid)
                related_ids.append(pid)
                if len(related_ids) >= cap:
                    break

        if not related_ids:
            continue

        rel_objs = [_snap_dict(snapshots[rid]) for rid in related_ids if rid in snapshots]
        top_cnt = co_map.get(aid, [])[0][1] if co_map.get(aid) else 0
        bundle_candidates.append(
            {
                "anchor": _snap_dict(anchor),
                "related": rel_objs,
                "affinity_note": f"Co-purchase / category neighbors (top pair sales: {top_cnt}).",
            },
        )

    if not bundle_candidates and anchor_ids:
        warnings.append("Anchors found but no related items — try a longer lookback or lower filters.")

    return PromotionSignals(bundle_candidates=bundle_candidates, warnings=warnings)
