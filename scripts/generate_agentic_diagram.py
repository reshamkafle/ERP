#!/usr/bin/env python3
"""Generate beginner-friendly agentic ERP flow diagrams as PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT_DUAL = ROOT / "output" / "agentic-purchases-promotions.png"
OUT_PRINT = ROOT / "output" / "agentic-reorder-print.png"

BG = "#f1f5f9"
GREEN = "#059669"
GREEN_LIGHT = "#d1fae5"
GREEN_MID = "#ecfdf5"
PURPLE = "#7c3aed"
PURPLE_LIGHT = "#ede9fe"
PURPLE_MID = "#f5f3ff"
AMBER = "#d97706"
AMBER_LIGHT = "#fef3c7"
BLUE = "#0284c7"
BLUE_LIGHT = "#e0f2fe"
SLATE = "#334155"
MUTED = "#64748b"


def rounded_box(ax, x, y, w, h, *, fc, ec, lw=2.0, radius=0.015):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad=0.012,rounding_size={radius}",
            linewidth=lw,
            edgecolor=ec,
            facecolor=fc,
            zorder=2,
        )
    )


def step_badge(ax, cx, cy, num: str, color: str, *, radius: float, fontsize: float):
    ax.add_patch(Circle((cx, cy), radius, facecolor=color, edgecolor="white", linewidth=3, zorder=5))
    ax.text(cx, cy, num, ha="center", va="center", fontsize=fontsize, weight="bold", color="white", zorder=6)


def down_arrow(ax, x, y_top, y_bottom, color=MUTED, *, scale: float = 18, lw: float = 2.5):
    ax.add_patch(
        FancyArrowPatch(
            (x, y_top),
            (x, y_bottom),
            arrowstyle="-|>",
            mutation_scale=scale,
            linewidth=lw,
            color=color,
            zorder=1,
        )
    )


def step_height(num_lines: int, *, title_fs: float, body_fs: float) -> float:
    """Axis-unit height from line count (tuned for dual-flow canvas)."""
    title_band = 0.038 + (title_fs - 10) * 0.002
    line_band = num_lines * (0.024 + (body_fs - 9) * 0.0012)
    padding = 0.022
    return title_band + line_band + padding


def card(
    ax,
    x,
    y,
    w,
    h,
    title: str,
    lines: list[str],
    *,
    fc,
    ec,
    title_color,
    title_fs: float,
    body_fs: float,
):
    rounded_box(ax, x, y, w, h, fc=fc, ec=ec)
    title_y = y + h - 0.014
    ax.text(x + w / 2, title_y, title, ha="center", va="top", fontsize=title_fs, weight="bold", color=title_color)
    body_top = title_y - 0.032 - (title_fs - 10) * 0.001
    body = "\n".join(lines)
    ax.text(x + 0.02, body_top, body, ha="left", va="top", fontsize=body_fs, color=SLATE, linespacing=1.55)


def column_header(
    ax,
    x,
    w,
    y,
    h: float,
    title: str,
    subtitle: str,
    color: str,
    bg: str,
    *,
    title_fs: float,
    sub_fs: float,
):
    rounded_box(ax, x, y, w, h, fc=bg, ec=color, lw=2.5)
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center", fontsize=title_fs, weight="bold", color=color)
    ax.text(x + w / 2, y + h * 0.22, subtitle, ha="center", va="center", fontsize=sub_fs, color=MUTED)


def _column_content_height(
    steps: list[tuple[str, list[str], str, str]],
    *,
    gap: float,
    title_fs: float,
    body_fs: float,
) -> float:
    total = sum(step_height(len(lines), title_fs=title_fs, body_fs=body_fs) for _, lines, _, _ in steps)
    return total + gap * max(0, len(steps) - 1)


def _draw_step_column(
    ax,
    *,
    col_x: float,
    col_w: float,
    steps: list[tuple[str, list[str], str, str]],
    accent: str,
    y_top: float,
    title_fs: float = 11,
    body_fs: float = 9.5,
    gap: float = 0.016,
) -> float:
    """Draw numbered steps top-to-bottom; return lowest y (for footer placement)."""
    card_x = col_x + 0.055
    card_w = col_w - 0.06
    badge_x = col_x + 0.028
    arrow_x = col_x + col_w / 2
    y_cursor = y_top  # top edge of current card

    for i, (title, lines, fc, ec) in enumerate(steps):
        h = step_height(len(lines), title_fs=title_fs, body_fs=body_fs)
        y_bottom = y_cursor - h
        color = accent if i < len(steps) - 1 else AMBER
        title_color = accent if i < len(steps) - 1 else AMBER
        step_badge(ax, badge_x, y_cursor - 0.026, str(i + 1), color, radius=0.02, fontsize=10)
        card(
            ax, card_x, y_bottom, card_w, h, title, lines,
            fc=fc, ec=ec, title_color=title_color, title_fs=title_fs, body_fs=body_fs,
        )
        if i < len(steps) - 1:
            arrow_top = y_bottom - 0.003
            arrow_bottom = y_bottom - gap + 0.003
            down_arrow(ax, arrow_x, arrow_top, arrow_bottom, color, scale=14, lw=2)
            y_cursor = y_bottom - gap
        else:
            y_cursor = y_bottom

    return y_cursor


def generate_dual_flow() -> None:
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(20, 18))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(BG)

    # --- Top: title + primer (fixed bands, no overlap) ---
    rounded_box(ax, 0.05, 0.935, 0.9, 0.052, fc="white", ec=SLATE, lw=1.5)
    ax.text(0.5, 0.968, "How AI Helps Your Store - Simple Guide", ha="center", fontsize=22, weight="bold", color="#0f172a")
    ax.text(
        0.5, 0.945,
        "Left = buying stock (Purchases)   |   Right = sales offers (Promotions)",
        ha="center", fontsize=11, color=MUTED,
    )

    rounded_box(ax, 0.05, 0.855, 0.9, 0.072, fc=BLUE_LIGHT, ec=BLUE, lw=2)
    ax.text(0.5, 0.912, 'What does "agentic AI" mean?', ha="center", fontsize=12, weight="bold", color=BLUE)
    ax.text(
        0.5, 0.878,
        "AI helpers read shop data and write a DRAFT plan.\n"
        "A manager must click Confirm before anything changes in the store.",
        ha="center", fontsize=10.5, color=SLATE, linespacing=1.55,
    )

    col_w = 0.43
    left_x = 0.05
    right_x = 0.52
    header_h = 0.048
    header_y = 0.748
    footer_reserve = 0.125

    # Color key (between primer and column headers)
    key_y, key_h = 0.802, 0.026
    keys = [
        (0.06, 0.28, "Steps 1-2: You click", GREEN_LIGHT, GREEN),
        (0.34, 0.28, "Steps 3-4: AI drafts", BLUE_LIGHT, BLUE),
        (0.62, 0.28, "Step 5: You approve", AMBER_LIGHT, AMBER),
    ]
    for kx, kw, label, fc, ec in keys:
        rounded_box(ax, kx, key_y, kw, key_h, fc=fc, ec=ec, lw=1.5)
        ax.text(kx + kw / 2, key_y + key_h / 2, label, ha="center", va="center", fontsize=9, weight="bold", color=SLATE)

    column_header(
        ax, left_x, col_w, header_y, header_h,
        "Smart Reordering",
        'Purchases  ->  "Run AI reorder"',
        GREEN, GREEN_LIGHT, title_fs=14, sub_fs=9,
    )
    column_header(
        ax, right_x, col_w, header_y, header_h,
        "Smart Promotions",
        'Promotions  ->  "Generate promotion proposals"',
        PURPLE, PURPLE_LIGHT, title_fs=14, sub_fs=9,
    )

    steps_top = header_y - 0.014

    purchase_steps = [
        ("You start it", ["Go to Purchases page", 'Click "Run AI reorder"', "Wait a few seconds"], GREEN_LIGHT, GREEN),
        (
            "Shop data is collected",
            ["Database check (no AI yet)", "Low stock, best sellers, promo boost items"],
            "white", "#94a3b8",
        ),
        (
            "Three AI helpers",
            ["Helper A: what is almost out?", "Helper B: what sells fast?", "Helper C: what is on promo?", "Team lead merges one list"],
            GREEN_MID, GREEN,
        ),
        ("Draft orders appear", ["One draft order per supplier", "Status stays DRAFT", "See reason for each line"], "white", "#94a3b8"),
        ("You decide", ["CONFIRM: stock increases", "DISCARD: remove draft", "Managers only"], AMBER_LIGHT, AMBER),
    ]

    promo_steps = [
        ("You start it", ["Go to Promotions page", "Click Generate proposals", "Optional: set lookback days"], PURPLE_LIGHT, PURPLE),
        ("Shop data is collected", ["Products bought together", "Recent sales for fair pricing"], "white", "#94a3b8"),
        ("AI helpers in a row", ["Helper 1: bundle ideas", "Helper 2: discount and duration", "Helper 3: final clean-up"], PURPLE_MID, PURPLE),
        ("Proposals to review", ["Bundles, percent off, dates", "Edit in the screen if needed", "Still a draft only"], "white", "#94a3b8"),
        ("You decide", ["CONFIRM: plan saved", "REJECT: start over"], AMBER_LIGHT, AMBER),
    ]

    step_gap = 0.014
    title_fs, body_fs = 10.5, 9.0
    needed_h = max(
        _column_content_height(purchase_steps, gap=step_gap, title_fs=title_fs, body_fs=body_fs),
        _column_content_height(promo_steps, gap=step_gap, title_fs=title_fs, body_fs=body_fs),
    )
    available_h = steps_top - footer_reserve
    if needed_h > available_h and available_h > 0:
        scale = available_h / needed_h
        title_fs = max(9.0, title_fs * scale)
        body_fs = max(8.0, body_fs * scale)
        step_gap = max(0.01, step_gap * scale)

    y_left = _draw_step_column(
        ax, col_x=left_x, col_w=col_w, steps=purchase_steps, accent=GREEN,
        y_top=steps_top, title_fs=title_fs, body_fs=body_fs, gap=step_gap,
    )
    y_right = _draw_step_column(
        ax, col_x=right_x, col_w=col_w, steps=promo_steps, accent=PURPLE,
        y_top=steps_top, title_fs=title_fs, body_fs=body_fs, gap=step_gap,
    )

    # Footer: fixed band at bottom (never overlaps steps)
    foot_h = 0.09
    foot_y = 0.022

    rounded_box(ax, 0.1, foot_y, 0.8, foot_h, fc="#fff7ed", ec="#ea580c", lw=2)
    ax.text(0.5, foot_y + foot_h - 0.016, "How they connect", ha="center", va="top", fontsize=12, weight="bold", color="#c2410c")
    ax.text(
        0.5, foot_y + foot_h / 2 - 0.008,
        'In Inventory, enable "Promotion reorder boost" on a product.\n'
        "That SKU gets extra priority when you Run AI reorder.",
        ha="center", va="center", fontsize=10, color=SLATE, linespacing=1.45,
    )

    divider_top = header_y + header_h
    ax.plot([0.5, 0.5], [foot_y + foot_h + 0.01, divider_top], color="#cbd5e1", linewidth=1.5, linestyle="--", zorder=0)

    OUT_DUAL.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DUAL, dpi=180, bbox_inches="tight", facecolor=BG, pad_inches=0.3)
    plt.close(fig)
    print(f"Wrote {OUT_DUAL}")


def generate_print_reorder_flow() -> None:
    """Single flow, large type - portrait page for printing (US Letter)."""
    plt.rcParams["font.family"] = "DejaVu Sans"

    # 8.5 x 11 in at 200 dpi
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    margin = 0.07
    col_w = 1 - 2 * margin
    x = margin

    # Title
    ax.text(0.5, 0.975, "Run AI Reorder", ha="center", fontsize=28, weight="bold", color="#0f172a")
    ax.text(
        0.5, 0.948,
        "How the Purchases AI works  (print-friendly)",
        ha="center", fontsize=14, color=MUTED,
    )

    rounded_box(ax, margin, 0.905, col_w, 0.038, fc=BLUE_LIGHT, ec=BLUE, lw=2)
    ax.text(
        0.5, 0.924,
        "Agentic AI = helpers draft a plan. YOU click Confirm before stock changes.",
        ha="center", fontsize=12, color=SLATE, weight="bold",
    )

    steps = [
        (
            "You start it",
            [
                "Open Purchases in the ERP app",
                'Press the "Run AI reorder" button',
                "Wait a few seconds",
            ],
            GREEN_LIGHT,
            GREEN,
        ),
        (
            "Shop data is collected",
            [
                "The database is checked first (no AI yet):",
                "- Products below low-stock level",
                "- Top sellers from the last 2 weeks",
                '- Products with "promotion boost" in Inventory',
            ],
            "white",
            "#94a3b8",
        ),
        (
            "Three AI helpers work together",
            [
                'Helper A asks: "What is almost out?"',
                'Helper B asks: "What sells fast?"',
                'Helper C asks: "What is on promotion?"',
                "A team lead merges one shopping list",
            ],
            GREEN_MID,
            GREEN,
        ),
        (
            "Draft purchase orders appear",
            [
                "One draft order per supplier",
                'Status stays DRAFT until you confirm',
                "Each line shows why it was suggested",
            ],
            "white",
            "#94a3b8",
        ),
        (
            "You decide (manager only)",
            [
                "CONFIRM  ->  stock increases in warehouse",
                "DISCARD  ->  delete that draft order",
                "Cashiers cannot run this feature",
            ],
            AMBER_LIGHT,
            AMBER,
        ),
    ]

    step_h = 0.122
    gap = 0.02
    y = 0.755
    badge_r = 0.028
    badge_fs = 18
    title_fs = 17
    body_fs = 13

    for i, (title, lines, fc, ec) in enumerate(steps):
        color = GREEN if i < 4 else AMBER
        step_badge(ax, x + 0.04, y + step_h - 0.04, str(i + 1), color, radius=badge_r, fontsize=badge_fs)
        card(
            ax, x + 0.08, y, col_w - 0.08, step_h,
            title, lines, fc=fc, ec=ec, title_color=color,
            title_fs=title_fs, body_fs=body_fs,
        )
        if i < len(steps) - 1:
            down_arrow(ax, 0.5, y - 0.008, y - gap - 0.012, color, scale=22, lw=3)
        y -= step_h + gap

    rounded_box(ax, margin, 0.045, col_w, 0.08, fc="#fff7ed", ec="#ea580c", lw=2)
    ax.text(0.5, 0.105, "Remember", ha="center", fontsize=15, weight="bold", color="#c2410c")
    ax.text(
        0.5, 0.072,
        "Draft = suggestion only.\n"
        "If AI is offline, simple rules still create drafts (e.g. order up to 2x low-stock level).",
        ha="center", fontsize=12, color=SLATE, linespacing=1.6,
    )

    OUT_PRINT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PRINT, dpi=200, bbox_inches="tight", facecolor="white", pad_inches=0.4)
    plt.close(fig)
    print(f"Wrote {OUT_PRINT}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate agentic ERP diagrams")
    parser.add_argument(
        "--mode",
        choices=["all", "dual", "print"],
        default="all",
        help="all = both files, dual = two-column guide, print = single large reorder flow",
    )
    args = parser.parse_args()
    if args.mode in ("all", "dual"):
        generate_dual_flow()
    if args.mode in ("all", "print"):
        generate_print_reorder_flow()


if __name__ == "__main__":
    main()
