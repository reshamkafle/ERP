# Manufacturing Operations

Full operational manufacturing: master data, MRP, production orders, shop floor, quality, costing, and inventory integration.

## API base

`/api/v1/manufacturing/`

Permissions: `manufacturing.ops.read` / `manufacturing.ops.write` (master/planning/quality/costing permissions also defined).

## Production order lifecycle

| Status | Transitions |
|--------|-------------|
| PLANNED | → RELEASED (`POST .../release`) |
| RELEASED | → IN_PROGRESS (`POST .../start`) |
| IN_PROGRESS | confirm, issue material, shop floor |
| IN_PROGRESS | → COMPLETED (`POST .../complete`) |
| COMPLETED | → CLOSED (`POST .../close`, posts variances) |

Create: `POST /production-orders` with `product_id`, `quantity_planned`, optional `routing_id`, warehouses.

Module-record `production_orders` JSON is deprecated; use the manufacturing API.

## MRP

- `POST /mrp/runs` — collects sales demand, forecasts, MPS lines; explodes BOM for component BUY/MAKE suggestions
- `POST /mrp/planned-orders/{id}/firm` — creates a production order from a MAKE planned order
- `POST /mrp/forecasts` — manual demand
- `GET /capacity/rccp` — rough-cut capacity by work center

## Quality & COA

- `POST /quality/plans` — inspection plan + characteristics
- `POST /quality/inspections` — record results (auto pass/fail on numeric limits)
- `POST /quality/coa/{plan_id}` — generates `CERTIFICATE_OF_ANALYSIS` ERP document

## Costing

- `POST /costing/standard/{product_id}` — rollup from BOM + routing work center rates
- Variances posted on MO close via `JournalSourceType.MANUFACTURING`

## Inventory

Material issue and FG receipt use warehouse-aware `stock_balances` with transaction types `PRODUCTION_ISSUE`, `PRODUCTION_RECEIPT`, `WIP_TRANSFER`.

Backflush runs on confirmation when `backflush: true`.

## UI

- `/manufacturing` — production order list + other feature module records
- `/manufacturing/orders/:id` — detail and lifecycle actions
- `/bom` — BOM editor (alternates/substitutes via API)
