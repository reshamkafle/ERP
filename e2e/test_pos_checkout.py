"""Point-of-sale checkout against a live API-backed product."""

import pytest

from pages.layout import AppLayout
from pages.pos import PosPage


pytestmark = pytest.mark.e2e


def test_pos_checkout_completes_sale(
    logged_in_admin: AppLayout,
    driver,
    base_url: str,
    wait_timeout: float,
    seeded_product: dict,
) -> None:
    pos = PosPage(driver, base_url, wait_timeout)
    pos.open().wait_loaded()

    pos.search_and_add_first(seeded_product["sku"])
    pos.checkout()
    pos.wait_receipt_dialog()

    assert f"Sale #" in driver.page_source
