#!/usr/bin/env python3
"""Capture Odoo demo4 UI metrics (colors, spacing) for ERP design tokens.

Usage (from repo root):
  python e2e/scripts/audit_odoo_ui.py
  ODOO_AUDIT_URL=https://demo4.odoo.com/odoo python e2e/scripts/audit_odoo_ui.py

Writes docs/ODOO-UI-REFERENCE.md (overwrites the measured section).
Requires: selenium, Chrome. No ERP stack needed.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

REPO_ROOT = Path(__file__).resolve().parents[2]
ODOO_URL = os.getenv("ODOO_AUDIT_URL", "https://demo4.odoo.com/odoo").rstrip("/")
HEADLESS = os.getenv("ODOO_AUDIT_HEADLESS", "true").lower() in ("1", "true", "yes")
OUT_DOC = REPO_ROOT / "docs" / "ODOO-UI-REFERENCE.md"


def _rgb_to_hex(rgb: str) -> str:
    """Convert 'rgb(r, g, b)' or 'rgba(...)' to #rrggbb when possible."""
    rgb = rgb.strip()
    if rgb.startswith("#"):
        return rgb.lower()
    if not rgb.startswith("rgb"):
        return rgb
    inner = rgb[rgb.index("(") + 1 : rgb.index(")")]
    parts = [p.strip() for p in inner.split(",")[:3]]
    try:
        r, g, b = (int(float(p)) for p in parts)
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, TypeError):
        return rgb


def _styles(driver: webdriver.Chrome, element) -> dict[str, str]:
    script = """
    const el = arguments[0];
    const s = getComputedStyle(el);
    return {
      backgroundColor: s.backgroundColor,
      color: s.color,
      fontSize: s.fontSize,
      fontFamily: s.fontFamily,
      fontWeight: s.fontWeight,
      width: s.width,
      height: s.height,
      padding: s.padding,
      borderColor: s.borderColor,
      borderRadius: s.borderRadius,
    };
    """
    raw = driver.execute_script(script, element)
    return {k: _rgb_to_hex(v) if "olor" in k or k == "backgroundColor" else v for k, v in raw.items()}


def _find_first(driver: webdriver.Chrome, selectors: list[str]):
    for sel in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                return els[0], sel
        except Exception:
            continue
    return None, None


def audit() -> dict:
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    metrics: dict = {"url": ODOO_URL, "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    try:
        driver.get(ODOO_URL)
        time.sleep(4)

        metrics["title"] = driver.title
        metrics["viewport"] = driver.get_window_size()

        body_el, body_sel = _find_first(driver, ["body", ".o_web_client", ".o_action_manager"])
        if body_el:
            metrics["body"] = {"selector": body_sel, "styles": _styles(driver, body_el)}

        nav_el, nav_sel = _find_first(
            driver,
            [
                ".o_main_navbar",
                "header.o_navbar",
                "nav",
                ".o_menu_sections",
                ".o_home_menu_background",
            ],
        )
        if nav_el:
            metrics["navbar"] = {"selector": nav_sel, "styles": _styles(driver, nav_el)}

        sidebar_el, sidebar_sel = _find_first(
            driver,
            [
                ".o_home_menu",
                ".o_apps_menu",
                "aside",
                ".o_action_manager",
            ],
        )
        if sidebar_el:
            metrics["sidebar_or_home"] = {"selector": sidebar_sel, "styles": _styles(driver, sidebar_el)}

        btn_el, btn_sel = _find_first(
            driver,
            [
                "button.btn-primary",
                ".btn-primary",
                "a.btn-primary",
                "button.o_form_button_save",
            ],
        )
        if btn_el:
            metrics["primary_button"] = {"selector": btn_sel, "styles": _styles(driver, btn_el)}

        metrics["page_source_length"] = len(driver.page_source)
    finally:
        driver.quit()

    return metrics


def write_reference_doc(metrics: dict) -> None:
    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)

    # ERP token targets derived from Odoo 17+ demo + measured values when present
    navbar_bg = metrics.get("navbar", {}).get("styles", {}).get("backgroundColor", "#714B67")
    body_bg = metrics.get("body", {}).get("styles", {}).get("backgroundColor", "#f0f0f0")

    measured_json = json.dumps(metrics, indent=2)

    content = f"""# Odoo UI reference (demo4)

Captured from [{metrics.get("url", ODOO_URL)}]({metrics.get("url", ODOO_URL)}) via `e2e/scripts/audit_odoo_ui.py`.

**Last audit:** {metrics.get("captured_at", "manual")}

## Design targets for ERP tokens

| Token | Value | Usage |
|-------|-------|-------|
| Sidebar background | `{navbar_bg}` / `oklch(0.42 0.09 330)` | Left app menu |
| Workspace background | `{body_bg}` / `oklch(0.96 0 0)` | Main content canvas |
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

```json
{measured_json}
```

## Re-run audit

```bash
cd e2e && pip install -r requirements.txt
python scripts/audit_odoo_ui.py
```
"""
    OUT_DOC.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT_DOC}")


def main() -> int:
    try:
        metrics = audit()
    except Exception as exc:
        print(f"Audit failed ({exc}); writing fallback reference doc.", file=sys.stderr)
        metrics = {
            "url": ODOO_URL,
            "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "error": str(exc),
            "note": "Using documented Odoo 17 defaults",
        }
    write_reference_doc(metrics)
    return 0


if __name__ == "__main__":
    sys.exit(main())
