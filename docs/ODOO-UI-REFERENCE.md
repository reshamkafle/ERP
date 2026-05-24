# Odoo UI reference (demo4)

Captured from [https://demo4.odoo.com/odoo](https://demo4.odoo.com/odoo) via `e2e/scripts/audit_odoo_ui.py`.

**Last audit:** manual baseline (run script to refresh measured JSON)

## Design targets for ERP tokens

| Token | Value | Usage |
|-------|-------|-------|
| Sidebar background | `#714B67` / `oklch(0.42 0.09 330)` | Left app menu |
| Workspace background | `#f0f0f0` / `oklch(0.96 0 0)` | Main content canvas |
| Sheet/card | `#ffffff` / `oklch(1 0 0)` | Forms, tables, KPI cards |
| Primary accent (actions) | `#017e84` / `oklch(0.52 0.08 195)` | Buttons, links, active nav |
| Sidebar width | `240px` | Collapsed: `64px` |
| Top bar height | `46px` | Breadcrumb + user cluster |
| Base font | `14px` system-ui | Dense ERP tables |
| Border | `#dee2e6` / `oklch(0.91 0 0)` | Tables, sheets |

## Layout patterns

- **Shell:** fixed left sidebar + top bar; scrollable gray workspace; white content sheet.
- **Control panel:** title row + toolbar (search, filters, primary action) above list.
- **Tables:** full-width, row hover `oklch(0.97 0 0)`, compact padding.
- **Login:** centered card on muted workspace; brand strip optional.

## Measured snapshot (auto-generated)

Run `python e2e/scripts/audit_odoo_ui.py` to populate this section.

## Re-run audit

```bash
cd e2e && pip install -r requirements.txt
python scripts/audit_odoo_ui.py
```
