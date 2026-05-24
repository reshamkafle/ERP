# Inventory Style-Color-Size Matrix & Variant Management

## Scope

- **In scope:** Inventory product templates (styles), normalized Color/Size attribute masters, SKU matrix generation, and variant child products (`products.template_id`).
- **Out of scope:** Manufacturing BOM “style” SKUs (e.g. `STYLE-001` in `ManufacturingItem`). Those remain in the manufacturing module. An inventory template may optionally reference a manufacturing item SKU when creating variants (existing `manufacturing_item_sku` link on products).

## Concepts

| Entity | Purpose |
|--------|---------|
| `ProductTemplate` | Style master: shared name, category, SKU prefix, default pricing/UOM |
| `ProductAttribute` | Dimension type (`COLOR`, `SIZE`) |
| `AttributeValue` | Controlled values (e.g. Red, M) |
| `Product` (variant) | Sellable SKU row with `template_id`, `color_value_id`, `size_value_id` |

## SKU pattern

Matrix generation uses: `{sku_prefix}-{color_code}-{size_code}` (uppercased, sanitized).

## API

- `GET/POST /api/v1/inventory/templates`
- `GET/PATCH/DELETE /api/v1/inventory/templates/{id}`
- `GET /api/v1/inventory/templates/{id}/variants`
- `POST /api/v1/inventory/templates/{id}/generate-matrix`
- `GET/POST /api/v1/inventory/attributes`
- `POST /api/v1/inventory/attributes/{id}/values`

List inventory supports filters: `template_id`, `style_code`, `color`, `size`.
