# ERP Built Using Cursor IDE

![ERP Promo](output/erp-promo.png)

**A modern, production-ready MVP ERP monorepo** demonstrating professional full-stack architecture built at high speed using **Cursor IDE**.

**Tech Stack**  
**Backend**: FastAPI + Async SQLAlchemy + PostgreSQL  
**Frontend**: Vite + React 19 + TypeScript + Tailwind CSS + shadcn/ui  
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

Frontend proxies /api to the backend. Default admin: admin@example.com / changeme123
Health Check: GET http://localhost:8000/api/v1/health

###E2E Tests (Selenium + Chrome)
```bash
chmod +x scripts/run-e2e.sh
./scripts/run-e2e.sh
```

###📖 Project Philosophy
This ERP proves that speed and quality are not mutually exclusive. By intelligently leveraging Cursor IDE’s rules, agents, commands, hooks, and skills, we achieved enterprise-grade code quality with significantly accelerated development.

###🤝 Contributing
Contributions are welcome! Please read CONTRIBUTING.md before submitting a Pull Request.
📄 License
Distributed under the MIT License. See LICENSE for more information.