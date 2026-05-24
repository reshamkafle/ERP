# Fabric & Raw Material Tracking (Roll / Lot, Barcode / RFID)

Roll-level inventory is the authoritative quantity for fabrics and roll-tracked raw materials. Product-level `stock` is rolled up from active rolls for compatibility with sales and legacy screens.

## Enabling roll tracking

On the inventory item master, enable **Roll tracking (fabric)** (`roll_tracking_enabled`). Production material issues for that SKU require a `material_roll_id`.

## Workflows

### Receipt (GRN / manual)

- **API:** `POST /v1/material-rolls/receive` — single roll  
- **API:** `POST /v1/material-rolls/bulk-receive` — multiple rolls per line  
- **API:** `POST /v1/material-rolls/purchase-receive` — rolls from a purchase order  

Each receipt auto-generates `roll_number` (`ROLL-YYYY-NNNNNN`) and sets `barcode` to the roll number unless overridden.

### Scan lookup

- **API:** `POST /v1/material-rolls/scan` with `barcode`, `rfid_tag`, or `roll_number`  
- Updates `last_scanned_at` and `last_scanned_by_id` for audit  

Handheld scanners can POST to this endpoint or use keyboard-wedge input in the UI (**Fabric rolls** page).

### Transfer, issue, return, quarantine

| Action | Endpoint |
|--------|----------|
| Transfer | `POST /v1/material-rolls/{id}/transfer` |
| Issue (partial meters) | `POST /v1/material-rolls/{id}/issue` |
| Return | `POST /v1/material-rolls/{id}/return` |
| Quarantine | `POST /v1/material-rolls/{id}/quarantine` |

### Production consumption

When issuing materials to a production order, pass `material_roll_id` in `MaterialIssueIn` for roll-tracked products. The roll `remaining_quantity` decreases; inventory transactions link via `material_roll_id`.

### Cut planning

Cut order fabric allocations accept `material_roll_id` (optional). Allocated meters cannot exceed roll `remaining_quantity`.

### Labels

- `GET /v1/material-rolls/{id}/label` — JSON + HTML payload  
- `GET /v1/material-rolls/{id}/label/print` — printable HTML  

### Traceability

`GET /v1/material-rolls/{id}/traceability` — backward (supplier, PO, receipt) and forward (issues to production/cut).

## Permissions

- `warehouse.material_rolls.read`  
- `warehouse.material_rolls.write`  

## UI

Navigate to **Inventory → Fabric rolls** (`/inventory/fabric-rolls`).

## Field reference (roll master)

Identification: `roll_number`, `barcode`, `rfid_tag`, `serial_number`, `product_id`  
Specs: `composition`, `color`, `dye_lot`, `gsm`, `width`, `finish_type`, `grade`  
Quantities: `initial_quantity`, `remaining_quantity`, `primary_uom`  
Sourcing: `supplier_id`, `supplier_lot_number`, `purchase_id`, `grn_reference`, `invoice_number`  
Status: `status`, `warehouse_id`, `location_id`, `quality_status`  
QC: `inspection_passed`, `certifications`, `defect_log`, `shrinkage_test_data` (JSON)  
Audit: `attachments`, `last_scanned_at`, `last_scanned_by_id`
