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