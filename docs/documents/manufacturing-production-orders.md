# Manufacturing / Production Orders

Production orders are **operational work orders** stored in `production_orders`, not in `module_records.extra_data.production`.

## API

- `GET/POST /api/v1/manufacturing/production-orders`
- `GET/PATCH /api/v1/manufacturing/production-orders/{id}`
- Actions: `release`, `start`, `issue-material`, `confirm`, `shop-floor`, `complete`, `close`

## Header fields

| Field | Description |
|-------|-------------|
| `order_number` | Auto `MO-{year}-{seq}` if omitted |
| `status` | PLANNED → RELEASED → IN_PROGRESS → COMPLETED → CLOSED |
| `product_id` | Finished/semi-finished product |
| `quantity_planned` / `quantity_completed` / `quantity_scrapped` / `quantity_rework` | Quantities |
| `start_date` / `end_date` | Schedule |
| `bom_parent_item_id` / `routing_id` / `production_version_id` | Master data links |
| `warehouse_id` / `wip_warehouse_id` | FG receipt and WIP |
| `creation_source` | MANUAL, MRP, SALES |

## Operations

Copied from routing on create when `routing_id` is set (`production_order_operations`).

## Legacy module records

The previous 14-section plant profile under `extra_data.production` is retired. Creating `feature_code=production_orders` via `/erp-modules` returns HTTP 400 with a pointer to the manufacturing API.

See [MANUFACTURING-OPS.md](../MANUFACTURING-OPS.md) for MRP, quality, costing, and inventory rules.
