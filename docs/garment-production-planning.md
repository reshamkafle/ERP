# Garment Production Planning & Scheduling

Phase 2 MVP: Advanced Production Planning (APS), CMT contracts, cut orders, and automated line balancing.

## Features

| Feature | Description |
|---------|-------------|
| **Production plans** | Style–color–size matrix from sales orders; schedule and release |
| **CMT / FOB** | Production contracts; buyer-supplied materials for CMT |
| **Cut orders** | Fabric cutting instructions with marker, plies, size breakdown |
| **Line balancing** | SMV-based takt, greedy auto-assign to stations, manual override |

## API base

`/api/v1/manufacturing/`

Permissions: `manufacturing.planning.read` / `manufacturing.planning.write` (also accepts `manufacturing.ops.*`).

### Production contracts (CMT / FOB)

- `GET/POST /contracts`
- `GET/PATCH /contracts/{id}`

### Production plans

- `GET/POST /planning/plans`
- `POST /planning/plans/from-sales` — explode sales order lines to variant SKUs
- `GET/PATCH /planning/plans/{id}`
- `POST /planning/plans/{id}/schedule` — auto-schedule sewing lines
- `POST /planning/plans/{id}/release` — cut orders + production orders + line balance session

### Cut orders

- `GET/POST /cut-orders`
- `GET/PATCH /cut-orders/{id}`
- `POST /cut-orders/{id}/complete` — updates plan line `quantity_cut`

### Line balancing

- `POST /line-balancing/calculate` — preview without save
- `POST /line-balancing/sessions` — persist session + assignments
- `GET /line-balancing/sessions/{id}`
- `PATCH /line-balancing/sessions/{id}/assignments/{assignment_id}` — manual station override

### Sewing lines

- `GET/POST /sewing-lines`

## CMT rules

- Material issues on production orders with a CMT contract validate against buyer-supplied quantities.
- MRP skips BUY planned orders for items on any active CMT material supply list.

## UI

- `/manufacturing/planning` — plan list, variant matrix, cut orders, schedule/release actions

## Related

- [MANUFACTURING-OPS.md](MANUFACTURING-OPS.md) — production orders, MRP, shop floor
- [inventory-variant-matrix.md](inventory-variant-matrix.md) — style–color–size SKUs
- [documents/bill-of-materials.md](documents/bill-of-materials.md) — fabric explosion for cut orders
