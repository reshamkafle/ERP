# ERP Built Using Cursor IDE

![ERP Promo](output/erp-promo.png)

**A modern, production-ready MVP ERP monorepo** demonstrating professional full-stack architecture built at high speed using **Cursor IDE**.

**Tech Stack**  
**Backend**: FastAPI + Async SQLAlchemy + PostgreSQL  
**Frontend**: Vite + React 19 + TypeScript + Tailwind CSS + shadcn/ui (Odoo-inspired shell: purple sidebar, teal accents, gray workspace)  
**Auth**: JWT with bcrypt password hashing (Python 3.12+ compatible)

---

## ✨ Key Highlights

- Complete MVP ERP with core modules (Dashboard, Inventory, Sales/POS, Customers, etc.)
- Clean monorepo architecture with separate backend & frontend
- Built rapidly using Cursor IDE’s AI acceleration tools
- Production-grade patterns, security, and testing
- **Agentic AI** for smart purchasing and promotions (LangGraph multi-agent workflows with human approval)

---

## 🤖 Agentic AI in this ERP

![How AI helps your store — purchases and promotions](output/agentic-purchases-promotions.png)

This ERP includes two **agentic** features: **Smart Reordering** on the Purchases page (`Run AI reorder`) and **Smart Promotions** on the Promotions page (`Generate promotion proposals`). The diagram above shows the full flow for both.

### What is agentic AI?

**Agentic AI** means software that acts like a small team of specialists—not one generic chat reply. Each specialist has a focused job (for example: low stock, fast sellers, or promotional SKUs). They read structured shop data, propose a **draft** plan, and a **supervisor** agent merges their output. Nothing is applied automatically: a **manager must confirm** before stock changes or promotion plans are saved.

In this project, that pattern is **human-in-the-loop (HITL)**: AI suggests, humans decide.

### Tech stack used for agents

| Layer | Technology | Role |
|-------|------------|------|
| **Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) | Stateful graphs: parallel specialists (procurement) or sequential chain (promotions) + supervisor merge |
| **LLM integration** | LangChain + `langchain-openai` `ChatOpenAI` | OpenAI-compatible API (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` in `.env`) — works with Ollama, vLLM, LiteLLM, etc. |
| **Structured output** | Pydantic models | Reliable JSON: line quantities, discount proposals, merge notes |
| **Signals (no LLM)** | PostgreSQL + SQLAlchemy | Deterministic inputs: low stock, sales velocity, co-purchase bundles, `promotion_reorder_boost` flags |
| **API** | FastAPI | `POST /api/v1/procurement-runs`, `POST /api/v1/promotion-runs`, confirm/reject endpoints |
| **Persistence** | PostgreSQL | `ProcurementRun`, `PromotionRun`, draft purchases with `agent_metadata` / `proposals_json` |
| **UI** | React 19 + TanStack Query | Purchases and Promotions pages; managers review drafts before confirm |
| **Fallback** | Rule-based merge | If the LLM is unavailable, simple rules still produce draft suggestions |

Key backend modules: `backend/app/agents/procurement_graph.py`, `promotion_graph.py`, `backend/app/services/procurement_signals.py`, `promotion_signals.py`, and `*_runner.py` services.

### How it helps your store

**Smart Reordering (Purchases)**

- Surfaces what to buy from **low stock**, **recent sales**, and **promotion-boost** products.
- Creates **draft purchase orders** grouped by each product’s default supplier, with a rationale per line.
- Managers **Confirm** to receive stock or **Discard** drafts they disagree with—no silent inventory changes.

**Smart Promotions**

- Suggests **bundles**, **discounts**, and **duration** from products often bought together and recent sales.
- Stores proposals as **DRAFT_REVIEW** so you can edit before **Confirm promotion plan** or **Reject**.

**Safety and operations**

- **Role-gated**: only Admin/Manager runs agents; cashiers use POS only.
- **Audit-friendly**: runs and drafts are tied to `procurement_run_id` / promotion run records.
- **Inventory link**: enabling **Promotion / campaign reorder boost** on a SKU gives it higher priority in AI reorder so you are less likely to stock out during a campaign.

Configure the LLM in `backend/.env` (see `.env.example`). Leave `LLM_BASE_URL` empty to use **rule-only** fallbacks. For a single-flow print diagram, see `output/agentic-reorder-print.png`.

---

## ⚡ Cursor IDE Acceleration Features Used

| Feature          | Description                                                                 | Key Benefit |
|------------------|-----------------------------------------------------------------------------|-----------|
| **Cursor Rules** | Project-wide instructions and coding standards enforced by AI               | Consistent code style, architecture adherence, and reduced review time |
| **Agents**       | Specialized AI agents for different domains (backend, frontend, testing)    | Parallel development, expert-level assistance per layer |
| **Commands**     | Custom reusable AI commands for repetitive tasks                            | Dramatic speed-up in scaffolding, refactoring, and boilerplate |
| **Hooks**        | Automated triggers that run on file changes or specific events              | Real-time quality control and instant feedback |
| **Rules**        | Fine-grained behavioral rules for AI responses                              | Precise control over generated code quality and patterns |
| **Skills**       | Pre-trained domain expertise injected into the model                        | Higher accuracy in complex ERP logic and business rules |

Project rules live under `.cursor/rules/` (stack, structure, auth, models, UI).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker (optional, for PostgreSQL)

### 1. Database
```bash
docker compose up -d postgres
cp .env.example backend/.env
```

Optional **agentic AI** (LangGraph + OpenAI-compatible LLM): set `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` in `backend/.env` (see `.env.example`). Leave `LLM_BASE_URL` empty to use rule-only draft suggestions. See [Agentic AI in this ERP](#agentic-ai-in-this-erp) for details.

###2. Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

###3.Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend proxies /api to the backend. For local dev only, set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `backend/.env` (see `.env.example`).
Health Check: GET http://localhost:8000/api/v1/health

### RBAC test users (50 roles / full permission coverage)

After the backend has started once (permissions and system roles are seeded), create 50 dev users with distinct roles—including document read/write/delete and every other permission code:

```bash
cd backend
python scripts/seed_rbac_users.py
```

Uses `SEED_USER_PASSWORD` from `backend/.env` (default `SeedUser123!`). Logins are `rbac-01-super-admin-a@seed.local` through `rbac-50-inventory-write@seed.local`. A credentials table is written to `backend/seed-output/rbac-users.md` (gitignored). Re-running the script is idempotent (skips existing emails).

### E2E Tests (Selenium + Chrome)
```bash
chmod +x scripts/run-e2e.sh
./scripts/run-e2e.sh
```

### Whole-system data seed (Selenium WebDriver)
Populate customers, suppliers, inventory, sales, procurement, CRM, TMS, module hubs, and more through the live UI (Chrome). Requires postgres, backend, and frontend running.

```bash
chmod +x scripts/run-system-seed.sh
./scripts/run-system-seed.sh
```

Optional: `E2E_SEED_COUNT=20` (records per entity type; default `10`). Reports are written to `e2e/reports/system_seed_report.{json,md}` with failure screenshots under `e2e/reports/screenshots/`.

### UI design reference (Odoo demo4)
Odoo-style layout tokens and an optional Selenium audit script live in [docs/ODOO-UI-REFERENCE.md](docs/ODOO-UI-REFERENCE.md). Re-capture demo metrics with:
```bash
python e2e/scripts/audit_odoo_ui.py
```

###📖 Project Philosophy
This ERP proves that speed and quality are not mutually exclusive. By intelligently leveraging Cursor IDE’s rules, agents, commands, hooks, and skills, we achieved enterprise-grade code quality with significantly accelerated development.

###🤝 Contributing
Contributions are welcome! Please read CONTRIBUTING.md before submitting a Pull Request.
📄 License
Distributed under the MIT License. See LICENSE for more information.

---

## 📄 ERP document journey

Operational and trade documents for manufacturing and export are catalogued in **[docs/ERP-DOCUMENT-JOURNEY.md](docs/ERP-DOCUMENT-JOURNEY.md)** and implemented in the app under **Documents** (`/documents`) with API `GET/POST /api/v1/erp-documents`. All 23 journey steps are stored in PostgreSQL (`erp_documents`) with blank `content` JSON until templates are defined.

---

## ✅ Phase 1 — Implemented

- **Multi-Level BOM** (Fabrics / Trims / Consumption / Wastage) — `/bom` with structure tree, material explosion, fabric & trim summaries, and BOM editor ([docs/documents/bill-of-materials.md](docs/documents/bill-of-materials.md))
- **Fabric & Raw Material Tracking** (Roll/Lot, Barcode/RFID) — `/inventory/fabric-rolls` with decimal roll quantities, scan API, GRN receipt, production issue, and traceability ([docs/fabric-roll-lot-tracking.md](docs/fabric-roll-lot-tracking.md))

---

## 🔮 Upcoming Features

### Phase 2: Core Enhancements ✅ (Completed)

![ERP Module Demo](output/promo_erp_demo.gif)

#### Original scope

- ✅ Style-Color-Size (SKU) Matrix + Variant Management — see [docs/inventory-variant-matrix.md](docs/inventory-variant-matrix.md)
- ✅ Multi-Level BOM (Fabrics/Trims/Consumption/Wastage) — see [docs/documents/bill-of-materials.md](docs/documents/bill-of-materials.md)
- ✅ Advanced Production Planning & Scheduling (Line balancing, CMT, Cut orders) — see [docs/garment-production-planning.md](docs/garment-production-planning.md)
- ✅ Fabric & Raw Material Tracking (Roll/Lot, Barcode/RFID) — see [docs/fabric-roll-lot-tracking.md](docs/fabric-roll-lot-tracking.md)
- ✅ Enhanced WMS
- ✅ Basic TMS Lite

#### Bonus — Featured Modules

- ✅ **Dashboards** — Executive dashboards with real-time analytics
- ✅ **Finance**
- ✅ **HCM / HR**
- ✅ **Procurement & Supplier Management**
- ✅ **Purchase & Warehouse Management**
- ✅ **Inventory & Variant Management**
- ✅ **Fabric Rolls Tracking**
- ✅ **Bill of Materials (BOM)**
- ✅ **Manufacturing & Production Planning**
- ✅ **SCM & TMS**
- ✅ **Sales & Distribution**
- ✅ **CRM & Customer Management**
- ✅ **POS, Promotions & Sales Order Processing**
- ✅ **Projects**
- ✅ **Access Control & User Management**
- ✅ **Advanced Reports & Analytics** across all modules

### Phase 3: Operations Optimization & Integration (Next 6-9 Months)

- Quality Control & Inspection (AQL, Mobile Audits)
- Subcontractor / Job Work Management
- Cut Planning & Marker Optimization
- Full TMS (GPS + Route Optimization)
- Fleet Management
- Advanced Order Fulfillment & Reverse Logistics
- MRP + Demand Forecasting
- Procurement & Supplier Portal

### Phase 4: Analytics, Compliance & Scalability (9-12+ Months)

- Real-time BI Dashboards & Predictive Analytics
- Barcode/RFID + Full Mobile Apps
- Finance & Compliance (Multi-currency, Exports, GST/VAT)
- Supply Chain Visibility Portal
- AI/ML Add-ons
- Third-Party Integrations (Accounting, E-commerce, EDI, IoT)