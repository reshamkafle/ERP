from decimal import Decimal
from unittest.mock import MagicMock

from app.core.html_escape import escape_html
from app.services.material_roll_service import build_label_html


def test_escape_html_neutralizes_script() -> None:
    assert "&lt;script&gt;" in escape_html('<script>alert("x")</script>')


def test_build_label_html_escapes_roll_fields() -> None:
    roll = MagicMock()
    roll.roll_number = 'R-<script>alert(1)</script>'
    roll.barcode = None
    roll.color = '<img src=x onerror=alert(1)>'
    roll.dye_lot = 'LOT_"test"'
    roll.remaining_quantity = Decimal("10.5")
    roll.primary_uom = "meter"

    product = MagicMock()
    product.sku = "SKU&1"
    product.name = "Fabric<script>"

    html = build_label_html(roll, product)
    assert "<script>" not in html
    assert "<img " not in html
    assert "&lt;script&gt;" in html
    assert "&lt;img " in html
