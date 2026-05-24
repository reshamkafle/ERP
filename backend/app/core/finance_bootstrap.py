"""Idempotent finance schema sync when DB was created via create_all before Alembic."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.models.base import Base

# Import finance models so metadata includes new tables
import app.models  # noqa: F401


SALES_COLUMNS = (
    ("subtotal", "NUMERIC(14, 2) NOT NULL DEFAULT 0"),
    ("tax_amount", "NUMERIC(14, 2) NOT NULL DEFAULT 0"),
    ("total", "NUMERIC(14, 2) NOT NULL DEFAULT 0"),
    ("amount_paid", "NUMERIC(14, 2) NOT NULL DEFAULT 0"),
    (
        "payment_status",
        "documentpaymentstatus NOT NULL DEFAULT 'PAID'::documentpaymentstatus",
    ),
    ("currency_code", "VARCHAR(3) NOT NULL DEFAULT 'USD'"),
)

PURCHASE_COLUMNS = (
    ("total", "NUMERIC(14, 2) NOT NULL DEFAULT 0"),
    ("amount_paid", "NUMERIC(14, 2) NOT NULL DEFAULT 0"),
    (
        "payment_status",
        "documentpaymentstatus NOT NULL DEFAULT 'UNPAID'::documentpaymentstatus",
    ),
    ("currency_code", "VARCHAR(3) NOT NULL DEFAULT 'USD'"),
)

FINANCE_ENUMS = (
    "CREATE TYPE taxtype AS ENUM ('VAT', 'GST', 'SALES_TAX', 'WITHHOLDING', 'OTHER')",
    "CREATE TYPE documentpaymentstatus AS ENUM ('UNPAID', 'PARTIAL', 'PAID')",
    "CREATE TYPE paymentdirection AS ENUM ('INBOUND', 'OUTBOUND')",
    "CREATE TYPE paymenttype AS ENUM ('CUSTOMER_RECEIPT', 'SUPPLIER_PAYMENT', 'PAYROLL', 'EXPENSE', 'OTHER')",
    "CREATE TYPE paymentstatus AS ENUM ('DRAFT', 'PENDING_APPROVAL', 'CONFIRMED', 'CANCELLED')",
    "CREATE TYPE partytype AS ENUM ('CUSTOMER', 'SUPPLIER', 'EMPLOYEE')",
    "CREATE TYPE allocationtype AS ENUM ('INVOICE', 'DISCOUNT', 'OVERPAYMENT', 'WRITE_OFF')",
    "CREATE TYPE accounttype AS ENUM ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')",
    "CREATE TYPE journalentrystatus AS ENUM ('DRAFT', 'POSTED', 'REVERSED')",
    "CREATE TYPE journalsourcetype AS ENUM ('PAYMENT', 'SALE', 'PURCHASE', 'MANUAL')",
)


async def _enum_exists(conn: AsyncConnection, name: str) -> bool:
    result = await conn.execute(
        text("SELECT 1 FROM pg_type WHERE typname = :name"),
        {"name": name},
    )
    return result.scalar() is not None


async def _ensure_enums(conn: AsyncConnection) -> None:
    enum_names = (
        "taxtype",
        "documentpaymentstatus",
        "paymentdirection",
        "paymenttype",
        "paymentstatus",
        "partytype",
        "allocationtype",
        "accounttype",
        "journalentrystatus",
        "journalsourcetype",
    )
    for ddl, name in zip(FINANCE_ENUMS, enum_names, strict=True):
        if not await _enum_exists(conn, name):
            await conn.execute(text(ddl))


async def _add_column_if_missing(
    conn: AsyncConnection,
    table: str,
    column: str,
    ddl: str,
) -> None:
    def _check(sync_conn):
        insp = inspect(sync_conn)
        cols = {c["name"] for c in insp.get_columns(table)}
        return column not in cols

    missing = await conn.run_sync(_check)
    if missing:
        await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))


async def sync_finance_schema(conn: AsyncConnection) -> None:
    await _ensure_enums(conn)

    for col, typ in SALES_COLUMNS:
        await _add_column_if_missing(conn, "sales", col, typ)
    for col, typ in PURCHASE_COLUMNS:
        await _add_column_if_missing(conn, "purchases", col, typ)

    await conn.run_sync(Base.metadata.create_all)

    # Backfill sale totals from line items when columns were just added
    await conn.execute(
        text(
            "UPDATE sales s SET subtotal = COALESCE((SELECT SUM(si.quantity * si.price_at_sale) "
            "FROM sale_items si WHERE si.sale_id = s.id), 0), "
            "total = COALESCE((SELECT SUM(si.quantity * si.price_at_sale) "
            "FROM sale_items si WHERE si.sale_id = s.id), 0) "
            "WHERE s.total = 0 AND EXISTS (SELECT 1 FROM sale_items si WHERE si.sale_id = s.id)"
        ),
    )
    await conn.execute(
        text(
            "UPDATE purchases p SET total = COALESCE((SELECT SUM(pi.quantity * pi.unit_cost) "
            "FROM purchase_items pi WHERE pi.purchase_id = p.id), 0) "
            "WHERE p.total = 0 AND EXISTS (SELECT 1 FROM purchase_items pi WHERE pi.purchase_id = p.id)"
        ),
    )

    # Seed COA and payment methods if empty
    coa_count = (await conn.execute(text("SELECT COUNT(*) FROM chart_of_accounts"))).scalar() or 0
    pm_count = (await conn.execute(text("SELECT COUNT(*) FROM payment_methods"))).scalar() or 0

    if coa_count == 0:
        coa_rows = [
            ("1000", "Cash", "ASSET"),
            ("1010", "Bank", "ASSET"),
            ("1100", "Accounts Receivable", "ASSET"),
            ("2000", "Accounts Payable", "LIABILITY"),
            ("2100", "Tax Payable", "LIABILITY"),
            ("2200", "Customer Deposits", "LIABILITY"),
            ("4000", "Sales Revenue", "REVENUE"),
            ("5000", "Purchase Expense", "EXPENSE"),
            ("5100", "Sales Discounts", "EXPENSE"),
            ("5200", "Purchase Discounts", "EXPENSE"),
        ]
        for code, name, atype in coa_rows:
            await conn.execute(
                text(
                    "INSERT INTO chart_of_accounts (code, name, account_type, is_postable, is_active) "
                    "VALUES (:code, :name, CAST(:atype AS accounttype), true, true)"
                ),
                {"code": code, "name": name, "atype": atype},
            )

    if pm_count == 0:
        methods = [
            ("CASH", "Cash", "1000"),
            ("BANK_TRANSFER", "Bank Transfer", "1010"),
            ("CHEQUE", "Cheque", "1010"),
            ("CARD", "Credit Card", "1010"),
            ("UPI", "UPI", "1010"),
            ("WALLET", "Digital Wallet", "1010"),
        ]
        for mcode, mname, gl_code in methods:
            await conn.execute(
                text(
                    "INSERT INTO payment_methods (code, name, gl_account_id, is_active) "
                    "SELECT :mcode, :mname, id, true FROM chart_of_accounts WHERE code = :gl_code"
                ),
                {"mcode": mcode, "mname": mname, "gl_code": gl_code},
            )

    settings_count = (await conn.execute(text("SELECT COUNT(*) FROM company_settings"))).scalar()
    if settings_count == 0:
        await conn.execute(
            text(
                "INSERT INTO company_settings (default_currency, base_currency, country_code, fiscal_year_start_month) "
                "VALUES ('USD', 'USD', 'US', 1)"
            ),
        )

    currency_count = (await conn.execute(text("SELECT COUNT(*) FROM currencies"))).scalar()
    if currency_count == 0:
        await conn.execute(
            text(
                "INSERT INTO currencies (code, name, symbol, decimal_places) VALUES "
                "('USD', 'US Dollar', '$', 2), ('NPR', 'Nepalese Rupee', 'Rs', 2)"
            ),
        )
