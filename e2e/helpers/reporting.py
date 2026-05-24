"""Structured reporting for ERPFlow document seed runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

E2E_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = E2E_ROOT / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"

KNOWN_GAPS = [
    {
        "document": "Delivery Order",
        "reason": "No standalone create UI; only /sales?delivery_filter=open list filter.",
    },
    {
        "document": "Production Planning / MRP",
        "reason": "No bulk create UI; MRP runs are API-driven.",
    },
    {
        "document": "RAW / FINISHED inventory (bulk seed)",
        "reason": "Multi-tab inventory form does not submit reliably for non-TRADING types in headless Chrome; seeded via API in system seed.",
    },
    {
        "document": "BOM garment SKUs (masters)",
        "reason": "Manufacturing item master has no create UI; parent SKUs use DB helper before Selenium BOM lines.",
    },
]


@dataclass
class SeedFailure:
    document_type: str
    index: int
    error: str
    screenshot_path: str | None = None


@dataclass
class SeedTypeResult:
    document_type: str
    label: str
    attempted: int
    succeeded: int
    failed: int
    failures: list[SeedFailure] = field(default_factory=list)


@dataclass
class SeedReport:
    started_at: str
    finished_at: str
    document_count_per_type: int
    type_results: list[SeedTypeResult]
    known_gaps: list[dict[str, str]] = field(default_factory=lambda: list(KNOWN_GAPS))

    @property
    def total_attempted(self) -> int:
        return sum(r.attempted for r in self.type_results)

    @property
    def total_succeeded(self) -> int:
        return sum(r.succeeded for r in self.type_results)

    @property
    def total_failed(self) -> int:
        return sum(r.failed for r in self.type_results)


def ensure_report_dirs() -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_report(report: SeedReport, *, basename: str = "erp_flow_seed_report") -> tuple[Path, Path]:
    ensure_report_dirs()
    json_path = REPORTS_DIR / f"{basename}.json"
    md_path = REPORTS_DIR / f"{basename}.md"

    payload = asdict(report)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(report, title=basename.replace("_", " ").title()), encoding="utf-8")
    return json_path, md_path


def _render_markdown(report: SeedReport, *, title: str = "ERPFlow Document Seed Report") -> str:
    lines = [
        f"# {title}",
        "",
        f"- **Started:** {report.started_at}",
        f"- **Finished:** {report.finished_at}",
        f"- **Target per type:** {report.document_count_per_type}",
        f"- **Total attempted:** {report.total_attempted}",
        f"- **Total succeeded:** {report.total_succeeded}",
        f"- **Total failed:** {report.total_failed}",
        "",
        "## Results by document type",
        "",
        "| Document type | Label | Attempted | Succeeded | Failed |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for result in report.type_results:
        lines.append(
            f"| {result.document_type} | {result.label} | {result.attempted} | "
            f"{result.succeeded} | {result.failed} |",
        )

    failures = [f for r in report.type_results for f in r.failures]
    if failures:
        lines.extend(["", "## Errors", ""])
        for failure in failures:
            lines.append(
                f"- **{failure.document_type} #{failure.index}:** {failure.error}",
            )
            if failure.screenshot_path:
                lines.append(f"  - Screenshot: `{failure.screenshot_path}`")

    lines.extend(["", "## Known gaps (not seeded)", ""])
    for gap in report.known_gaps:
        lines.append(f"- **{gap['document']}:** {gap['reason']}")

    return "\n".join(lines) + "\n"
