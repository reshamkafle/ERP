# Bill of Materials (BOM)

Multi-level BOM for garment manufacturing: headers, component lines, explosion, and inventory product linkage.

## Phase 1 fields

### BOM header (`bom_headers`)

| Field | Description |
|-------|-------------|
| `bom_number` | Unique identifier (default `{parent_sku}-V{version}`) |
| `version` | Increments on each save |
| `status` | `DRAFT`, `ACTIVE`, `OBSOLETE`, `SUPERSEDED` |
| `bom_type` | `MANUFACTURING`, `ENGINEERING`, `SALES`, `SERVICE`, `PHANTOM` |
| `effective_start_date` / `effective_end_date` | Optional effectivity window |
| `eco_number` | Engineering change order reference |
| `approved_at` / `approved_by_id` | Set when status moves to `ACTIVE` via PATCH |
| `created_by_id` / `updated_by_id` | Audit trail |

### BOM lines (`bom_lines`)

| Field | Description |
|-------|-------------|
| `line_sequence` | Sort order (unique per parent) |
| `quantity_per_unit` | Qty per parent assembly |
| `consumption_type` | `FABRIC`, `TRIM`, `OTHER` |
| `wastage_percentage` | Scrap / shrinkage % |
| `yield_percentage` | Optional yield % (0–100); inflates gross qty in explosion when below 100% |
| `is_phantom` | Flatten through child BOM without stocking phantom |
| `lead_time_offset_days` | Days before parent need date |
| `notes` | Free text |

### Item master (read-only on BOM UI)

Component details (supplier, HS code, weight, costs, traceability flags) come from the linked **inventory Product** when `manufacturing_items.product_id` is set. Edit those fields on the inventory item; the BOM API returns them as `product_snapshot` on each line.

## API

- `GET /v1/bom/{sku}` — BOM with header and enriched lines
- `POST /v1/bom/{sku}` — `SaveBOMRequest` (`header` optional, `lines` required)
- `PATCH /v1/bom/{sku}/status` — status workflow without rewriting lines
- Tree, explode, fabric/trim summaries unchanged

## UI

`/bom` — Bill of Materials page:

- **BOM list** — existing BOMs with **Edit**; **Styles without BOM** lists parents ready to create.
- **New BOM** — pick a finished good or sub-assembly that has no BOM yet.
- Read tabs: structure, materials, fabric, trims (require a saved BOM).
- **Create BOM** / **Edit BOM** tab when `warehouse.bom.write` is granted (save via `POST`, activate via `PATCH` status).

## Alternates & substitutes

- `POST /api/v1/bom/{sku}/alternates` — alternate BOM headers (group + priority)
- `POST /api/v1/bom/{sku}/lines/{line_id}/substitutes` — line-level substitute components
- Listed on `GET /api/v1/bom/{sku}` in `alternates` and per-line `substitutes`
- **Edit BOM** tab on `/bom` includes alternates & substitutes panels (requires saved BOM for line IDs)

Legacy manufacturing endpoints (`/api/v1/manufacturing/bom/...`) remain available.

## Deferred (Phase 2+)

Revision history side-by-side UI, attachments, configurable BOM parameters UI.
