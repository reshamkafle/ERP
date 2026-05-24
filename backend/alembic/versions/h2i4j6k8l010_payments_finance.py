"""payments and finance module

Revision ID: h2i4j6k8l010
Revises: g1h3i5j7k909
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "h2i4j6k8l010"
down_revision: Union[str, None] = "g1h3i5j7k909"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TAX_TYPES = ("VAT", "GST", "SALES_TAX", "WITHHOLDING", "OTHER")
DOC_PAYMENT_STATUSES = ("UNPAID", "PARTIAL", "PAID")
PAYMENT_DIRECTIONS = ("INBOUND", "OUTBOUND")
PAYMENT_TYPES = ("CUSTOMER_RECEIPT", "SUPPLIER_PAYMENT", "PAYROLL", "EXPENSE", "OTHER")
PAYMENT_STATUSES = ("DRAFT", "PENDING_APPROVAL", "CONFIRMED", "CANCELLED")
PARTY_TYPES = ("CUSTOMER", "SUPPLIER", "EMPLOYEE")
ALLOCATION_TYPES = ("INVOICE", "DISCOUNT", "OVERPAYMENT", "WRITE_OFF")
ACCOUNT_TYPES = ("ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE")
JOURNAL_STATUSES = ("DRAFT", "POSTED", "REVERSED")
JOURNAL_SOURCE_TYPES = ("PAYMENT", "SALE", "PURCHASE", "MANUAL")

COA_SEED = [
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

PAYMENT_METHOD_SEED = [
    ("CASH", "Cash", "1000"),
    ("BANK_TRANSFER", "Bank Transfer", "1010"),
    ("CHEQUE", "Cheque", "1010"),
    ("CARD", "Credit Card", "1010"),
    ("UPI", "UPI", "1010"),
    ("WALLET", "Digital Wallet", "1010"),
]


def _enum(name: str, values: tuple[str, ...]) -> postgresql.ENUM:
    e = postgresql.ENUM(*values, name=name, create_type=False)
    return e


def upgrade() -> None:
    bind = op.get_bind()
    for name, values in (
        ("taxtype", TAX_TYPES),
        ("documentpaymentstatus", DOC_PAYMENT_STATUSES),
        ("paymentdirection", PAYMENT_DIRECTIONS),
        ("paymenttype", PAYMENT_TYPES),
        ("paymentstatus", PAYMENT_STATUSES),
        ("partytype", PARTY_TYPES),
        ("allocationtype", ALLOCATION_TYPES),
        ("accounttype", ACCOUNT_TYPES),
        ("journalentrystatus", JOURNAL_STATUSES),
        ("journalsourcetype", JOURNAL_SOURCE_TYPES),
    ):
        postgresql.ENUM(*values, name=name).create(bind, checkfirst=True)

    tax_type = _enum("taxtype", TAX_TYPES)
    doc_pay = _enum("documentpaymentstatus", DOC_PAYMENT_STATUSES)
    pay_dir = _enum("paymentdirection", PAYMENT_DIRECTIONS)
    pay_type = _enum("paymenttype", PAYMENT_TYPES)
    pay_status = _enum("paymentstatus", PAYMENT_STATUSES)
    party_type = _enum("partytype", PARTY_TYPES)
    alloc_type = _enum("allocationtype", ALLOCATION_TYPES)
    acct_type = _enum("accounttype", ACCOUNT_TYPES)
    je_status = _enum("journalentrystatus", JOURNAL_STATUSES)
    je_source = _enum("journalsourcetype", JOURNAL_SOURCE_TYPES)

    op.create_table(
        "company_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("default_currency", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("base_currency", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("country_code", sa.String(length=2), nullable=False, server_default="US"),
        sa.Column("fiscal_year_start_month", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        sa.text(
            "INSERT INTO company_settings (default_currency, base_currency, country_code, fiscal_year_start_month) "
            "VALUES ('USD', 'USD', 'US', 1)"
        )
    )

    op.create_table(
        "tax_rates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("rate_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("tax_type", tax_type, nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tax_rates_code_country", "tax_rates", ["code", "country_code"])
    op.create_index("ix_tax_rates_effective", "tax_rates", ["effective_from", "effective_to"])

    op.create_table(
        "currencies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=3), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("symbol", sa.String(length=8), nullable=False, server_default="$"),
        sa.Column("decimal_places", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.execute(
        sa.text(
            "INSERT INTO currencies (code, name, symbol, decimal_places) VALUES "
            "('USD', 'US Dollar', '$', 2), ('NPR', 'Nepalese Rupee', 'Rs', 2)"
        )
    )

    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("from_currency", sa.String(length=3), nullable=False),
        sa.Column("to_currency", sa.String(length=3), nullable=False),
        sa.Column("rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("from_currency", "to_currency", "effective_date", name="uq_exchange_rates_pair_date"),
    )

    op.create_table(
        "chart_of_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("account_type", acct_type, nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("is_postable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["chart_of_accounts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_chart_of_accounts_code", "chart_of_accounts", ["code"])

    coa_table = sa.table(
        "chart_of_accounts",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("account_type", sa.String),
        sa.column("is_postable", sa.Boolean),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        coa_table,
        [
            {"code": c, "name": n, "account_type": t, "is_postable": True, "is_active": True}
            for c, n, t in COA_SEED
        ],
    )

    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("account_number", sa.String(length=64), nullable=True),
        sa.Column("gl_account_id", sa.Integer(), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["gl_account_id"], ["chart_of_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "payment_methods",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("gl_account_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["gl_account_id"], ["chart_of_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    for code, name, gl_code in PAYMENT_METHOD_SEED:
        op.execute(
            sa.text(
                "INSERT INTO payment_methods (code, name, gl_account_id, is_active) "
                "SELECT :code, :name, id, true FROM chart_of_accounts WHERE code = :gl_code"
            ).bindparams(code=code, name=name, gl_code=gl_code),
        )

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entry_number", sa.String(length=64), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("source_type", je_source, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("status", je_status, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reversal_of_id", sa.Integer(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["reversal_of_id"], ["journal_entries.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entry_number"),
    )
    op.create_index("ix_journal_entries_entry_number", "journal_entries", ["entry_number"])

    op.create_table(
        "journal_lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("journal_entry_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("debit", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("credit", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("memo", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["account_id"], ["chart_of_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_journal_lines_journal_entry_id", "journal_lines", ["journal_entry_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payment_number", sa.String(length=64), nullable=False),
        sa.Column("direction", pay_dir, nullable=False),
        sa.Column("payment_type", pay_type, nullable=False),
        sa.Column("status", pay_status, nullable=False),
        sa.Column("party_type", party_type, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("supplier_id", sa.Integer(), nullable=True),
        sa.Column("party_name", sa.String(length=255), nullable=True),
        sa.Column("payment_method_id", sa.Integer(), nullable=False),
        sa.Column("bank_account_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("exchange_rate", sa.Numeric(18, 8), nullable=True),
        sa.Column("amount_base", sa.Numeric(14, 2), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("reference", sa.String(length=128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("erp_document_id", sa.Integer(), nullable=True),
        sa.Column("journal_entry_id", sa.Integer(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("approved_by_id", sa.Integer(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"]),
        sa.ForeignKeyConstraint(["bank_account_id"], ["bank_accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["erp_document_id"], ["erp_documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approved_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_number"),
    )
    op.create_index("ix_payments_payment_number", "payments", ["payment_number"])

    op.create_table(
        "payment_allocations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("allocation_type", alloc_type, nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=True),
        sa.Column("purchase_id", sa.Integer(), nullable=True),
        sa.Column("allocated_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["purchase_id"], ["purchases.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "(sale_id IS NOT NULL AND purchase_id IS NULL) OR (sale_id IS NULL AND purchase_id IS NOT NULL) OR "
            "(sale_id IS NULL AND purchase_id IS NULL AND allocation_type IN ('OVERPAYMENT'))",
            name="ck_payment_allocations_target",
        ),
    )
    op.create_index("ix_payment_allocations_payment_id", "payment_allocations", ["payment_id"])

    op.create_table(
        "payment_audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("old_status", sa.String(length=32), nullable=True),
        sa.Column("new_status", sa.String(length=32), nullable=True),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payment_audit_logs_payment_id", "payment_audit_logs", ["payment_id"])

    op.add_column("sales", sa.Column("subtotal", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column("sales", sa.Column("tax_amount", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column("sales", sa.Column("total", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column("sales", sa.Column("amount_paid", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column(
        "sales",
        sa.Column("payment_status", doc_pay, nullable=False, server_default="PAID"),
    )
    op.add_column(
        "sales",
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
    )

    op.add_column("purchases", sa.Column("total", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column("purchases", sa.Column("amount_paid", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column(
        "purchases",
        sa.Column("payment_status", doc_pay, nullable=False, server_default="UNPAID"),
    )
    op.add_column(
        "purchases",
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
    )

    op.execute(
        sa.text(
            "UPDATE sales s SET subtotal = COALESCE((SELECT SUM(si.quantity * si.price_at_sale) "
            "FROM sale_items si WHERE si.sale_id = s.id), 0), "
            "total = COALESCE((SELECT SUM(si.quantity * si.price_at_sale) "
            "FROM sale_items si WHERE si.sale_id = s.id), 0)"
        )
    )
    op.execute(
        sa.text(
            "UPDATE purchases p SET total = COALESCE((SELECT SUM(pi.quantity * pi.unit_cost) "
            "FROM purchase_items pi WHERE pi.purchase_id = p.id), 0) "
            "WHERE p.status = 'RECEIVED'"
        )
    )


def downgrade() -> None:
    op.drop_column("purchases", "currency_code")
    op.drop_column("purchases", "payment_status")
    op.drop_column("purchases", "amount_paid")
    op.drop_column("purchases", "total")
    op.drop_column("sales", "currency_code")
    op.drop_column("sales", "payment_status")
    op.drop_column("sales", "amount_paid")
    op.drop_column("sales", "total")
    op.drop_column("sales", "tax_amount")
    op.drop_column("sales", "subtotal")
    op.drop_table("payment_audit_logs")
    op.drop_table("payment_allocations")
    op.drop_table("payments")
    op.drop_table("journal_lines")
    op.drop_table("journal_entries")
    op.drop_table("payment_methods")
    op.drop_table("bank_accounts")
    op.drop_table("chart_of_accounts")
    op.drop_table("exchange_rates")
    op.drop_table("currencies")
    op.drop_table("tax_rates")
    op.drop_table("company_settings")
    bind = op.get_bind()
    for name in (
        "journalsourcetype",
        "journalentrystatus",
        "accounttype",
        "allocationtype",
        "partytype",
        "paymentstatus",
        "paymenttype",
        "paymentdirection",
        "documentpaymentstatus",
        "taxtype",
    ):
        postgresql.ENUM(name=name).drop(bind, checkfirst=True)
