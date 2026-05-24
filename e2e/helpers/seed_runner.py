"""Shared seed loop utilities for Selenium system seeds."""

from __future__ import annotations

from collections.abc import Callable

from helpers.reporting import REPORTS_DIR, SCREENSHOTS_DIR, SeedFailure, SeedTypeResult, ensure_report_dirs
from selenium.webdriver.chrome.webdriver import WebDriver


def run_seed_type(
    *,
    driver: WebDriver,
    document_type: str,
    label: str,
    count: int,
    create_fn: Callable[[int], None],
) -> SeedTypeResult:
    result = SeedTypeResult(
        document_type=document_type,
        label=label,
        attempted=count,
        succeeded=0,
        failed=0,
    )
    ensure_report_dirs()

    for index in range(1, count + 1):
        try:
            create_fn(index)
            result.succeeded += 1
        except Exception as exc:  # noqa: BLE001 — collect all seed failures
            screenshot_path = SCREENSHOTS_DIR / f"{document_type}-{index}.png"
            try:
                driver.save_screenshot(str(screenshot_path))
                shot = str(screenshot_path.relative_to(REPORTS_DIR.parent))
            except OSError:
                shot = None
            result.failed += 1
            result.failures.append(
                SeedFailure(
                    document_type=document_type,
                    index=index,
                    error=str(exc),
                    screenshot_path=shot,
                ),
            )

    return result
