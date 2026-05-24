#!/usr/bin/env python3
"""
Record an ERP product walkthrough with Playwright and export an optimized promo GIF.

Usage:
    pip install playwright
    playwright install chromium
    python scripts/generate_promo_gif.py

Requires backend + frontend running (see scripts/dev.sh).
Output: output/promo_erp_demo.gif
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_GIF = ROOT / "output" / "promo_erp_demo.gif"

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:5173").rstrip("/")
ADMIN_EMAIL = os.getenv("E2E_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("E2E_ADMIN_PASSWORD", "changeme123")

VIEWPORT = {"width": 1280, "height": 720}


def jitter(base: float, spread: float = 0.25) -> float:
    return max(0.45, base + random.uniform(-spread, spread))


def require_playwright():
    try:
        from playwright.sync_api import Page, sync_playwright

        return Page, sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is required. Install with:\n"
            "  pip install playwright\n"
            "  playwright install chromium",
        ) from exc


def require_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg not found. Install with: brew install ffmpeg")
    return ffmpeg


def wait_heading(page, title: str | None = None, timeout: float = 15_000) -> None:
    if title:
        page.locator("h1").filter(has_text=title).first.wait_for(state="visible", timeout=timeout)
    else:
        page.locator("h1").first.wait_for(state="visible", timeout=timeout)


def wait_authenticated(page) -> None:
    page.wait_for_selector("[data-testid='app-sidebar']", timeout=20_000)


def pause(page, seconds: float) -> None:
    page.wait_for_timeout(int(jitter(seconds) * 1000))


def smooth_scroll(page, amount: int = 280) -> None:
    page.evaluate(
        """(dy) => window.scrollBy({ top: dy, behavior: 'smooth' })""",
        amount,
    )
    pause(page, 0.55)


def click_nav_slug(page, slug: str) -> None:
    link = page.locator(f"[data-testid='nav-{slug}']")
    link.scroll_into_view_if_needed()
    link.hover()
    pause(page, 0.35)
    link.click()
    pause(page, 0.15)


def visit(page, slug: str, heading: str | None = None, dwell: float = 0.9) -> None:
    click_nav_slug(page, slug)
    wait_heading(page, heading)
    pause(page, dwell)


def goto_module(page, path: str, heading: str | None = None) -> None:
    page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
    wait_authenticated(page)
    wait_heading(page, heading)
    pause(page, 1.0)


def login(page) -> None:
    page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
    wait_heading(page, "Sign in")
    pause(page, 1.4)
    page.fill("#email", ADMIN_EMAIL)
    pause(page, 0.35)
    page.fill("#password", ADMIN_PASSWORD)
    pause(page, 0.45)
    page.locator("button[type='submit']").click()
    wait_authenticated(page)
    wait_heading(page, "Dashboard")
    smooth_scroll(page, 180)
    pause(page, 1.6)


def run_tour(page) -> None:
    """Follow prompts/promo.md module flow."""
    # 2. Dashboard (already logged in)
    wait_heading(page, "Dashboard")
    smooth_scroll(page, 320)
    pause(page, 1.2)

    # 3. Finance
    visit(page, "finance", "Financial Management", 1.1)
    smooth_scroll(page, 240)

    # 4. HCM
    visit(page, "hcm", "Human Capital", 1.1)
    smooth_scroll(page, 220)

    # 5. Procurement → Suppliers → Purchases
    visit(page, "procurement", None, 0.95)
    visit(page, "suppliers", "Vendor master", 0.95)
    visit(page, "purchases", "Purchases", 0.95)

    # 6. Warehouse chain
    visit(page, "warehouses", "Warehouses", 0.85)
    visit(page, "locations", "Storage locations", 0.85)
    visit(page, "inventory", "Inventory", 0.85)
    visit(page, "inventory-variants", "Style–Color–Size matrix", 0.85)
    visit(page, "fabric-rolls", "Fabric rolls & lots", 0.85)

    # 7. Manufacturing → BOM → Production Planning
    visit(page, "manufacturing", "Manufacturing", 0.9)
    visit(page, "bom", "Bill of Materials", 0.9)
    visit(page, "manufacturing-planning", "Production Planning & Scheduling", 1.0)
    smooth_scroll(page, 200)

    # 8. Sales & Distribution → CRM → Customers → Sales → POS → Promotions
    visit(page, "sales-distribution", "Sales & Distribution", 0.8)
    visit(page, "crm", "Customer Relationship Management", 0.8)
    visit(page, "customers", "Customers", 0.8)
    visit(page, "sales", "Sales orders", 0.8)
    visit(page, "pos", "Point of sale", 0.8)
    visit(page, "promotions", "Promotions", 0.8)

    # 9. Projects
    visit(page, "projects", "Project Management", 1.0)

    # 10. Access control + Users
    visit(page, "settings-access", "Roles", 0.9)
    visit(page, "settings-users", "Users", 0.9)

    # 11. Reports → Dashboard finale
    visit(page, "reports", "Reports", 1.3)
    smooth_scroll(page, 260)
    visit(page, "dashboard", "Dashboard", 1.8)
    smooth_scroll(page, -400)


def convert_to_gif(
    ffmpeg: str,
    video_path: Path,
    out_path: Path,
    *,
    fps: int = 10,
    width: int = 720,
    speed: float = 1.55,
    max_duration: float = 15.0,
) -> None:
    """Convert WebM/MP4 to a palette-optimized GIF under ~5 MB."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _render(target: Path, render_fps: int, render_width: int, colors: int) -> None:
        palette = target.with_suffix(".palette.png")
        filters = (
            f"setpts={1 / speed:.4f}*PTS,"
            f"trim=duration={max_duration},"
            f"fps={render_fps},"
            f"scale={render_width}:-1:flags=lanczos,"
            f"split[s0][s1];[s0]palettegen=max_colors={colors}:stats_mode=diff[p];"
            f"[s1][p]paletteuse=dither=bayer:bayer_scale=4"
        )
        subprocess.run(
            [ffmpeg, "-y", "-i", str(video_path), "-vf", filters, str(target)],
            check=True,
            capture_output=True,
        )
        palette.unlink(missing_ok=True)

    _render(out_path, fps, width, 96)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    if size_mb > 5.0:
        tmp = out_path.with_suffix(".optimized.gif")
        _render(tmp, max(8, fps - 2), int(width * 0.82), 64)
        tmp.replace(out_path)
        size_mb = out_path.stat().st_size / (1024 * 1024)
    if size_mb > 5.0:
        tmp = out_path.with_suffix(".optimized.gif")
        _render(tmp, 8, 560, 48)
        tmp.replace(out_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ERP promo GIF")
    parser.add_argument("--output", type=Path, default=OUTPUT_GIF)
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", action="store_false", dest="headless")
    args = parser.parse_args()

    Page, sync_playwright = require_playwright()
    ffmpeg = require_ffmpeg()

    with tempfile.TemporaryDirectory(prefix="erp-promo-") as tmp:
        video_dir = Path(tmp) / "video"
        video_dir.mkdir()

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=args.headless)
            context = browser.new_context(
                viewport=VIEWPORT,
                record_video_dir=str(video_dir),
                record_video_size=VIEWPORT,
                color_scheme="light",
            )
            page = context.new_page()
            try:
                login(page)
                run_tour(page)
            finally:
                page.close()
                context.close()
                browser.close()

        videos = sorted(video_dir.glob("*.webm")) + sorted(video_dir.glob("*.mp4"))
        if not videos:
            print("No video file was recorded.", file=sys.stderr)
            return 1
        video_path = videos[-1]

        convert_to_gif(ffmpeg, video_path, args.output)
        size_mb = args.output.stat().st_size / (1024 * 1024)
        print(f"Saved {args.output} ({size_mb:.2f} MB)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
