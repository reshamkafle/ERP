# Access control

## Overview

The ERP uses **dynamic role-based access control (RBAC)** with:

- **Permission codes** (e.g. `warehouse.inventory.read`, `profile.layout.configure`)
- **Roles** with optional **department** (`accounting`, `warehouse`, `sales`, …) and **role type** (`SUPER_ADMIN`, `ADMIN`, `DIRECTOR`, `IT`, `EMPLOYEE`)
- **Delegation rule**: users may grant permissions to roles only if they already hold those permissions

## Role types

| Type | Purpose |
|------|---------|
| `SUPER_ADMIN` | Full access; seeded on install |
| `ADMIN` | Organization admin |
| `DIRECTOR` | Department leadership |
| `IT` | System configuration |
| `EMPLOYEE` | Standard staff (accounting, warehouse, sales, etc.) |

## Key permissions

| Code | Description |
|------|-------------|
| `system.roles.manage` | Edit roles and permission matrix (`/settings/access`) |
| `system.users.read` | View users, roles, and effective permissions (`/settings/users`) |
| `system.users.manage` | Assign roles to users (`/settings/users`) |
| `profile.layout.configure` | Edit personal layout (`/settings/layout`) |
| `accounting.records.*` | Financial records (accounting department) |
| `warehouse.*` | Inventory, BOM, purchases, suppliers, documents |
| `sales.*` | Customers, orders, POS, promotions |

## APIs

- `GET /api/v1/auth/me/permissions` — current user's effective permissions
- `GET /api/v1/access/permissions` — catalog (requires `system.roles.manage`)
- `GET/PUT /api/v1/access/roles/{id}/permissions` — with delegation check
- `GET /api/v1/access/users` — list users with roles and permissions (requires `system.users.read` or `system.users.manage`)
- `GET/POST/DELETE /api/v1/access/users/{id}/roles` — assign roles (requires `system.users.manage`)
- `PUT /api/v1/access/users/{id}/permissions` — toggle per-user permission overrides (requires `system.users.manage`)
- `GET/PATCH /api/v1/users/me/preferences` — layout (PATCH requires `profile.layout.configure`)

## Bootstrap

On startup, permissions and system roles are seeded. Legacy `users.role` (`ADMIN` / `MANAGER` / `CASHIER`) is mapped to **Super Admin**, **Manager**, and **Cashier** roles until explicit assignments exist.

## Frontend

- Sidebar and routes use `canAccess(permissions, code)`
- Missing permission → `/forbidden` and hidden nav links

## RBAC breach probe (manual)

Negative authorization test: each seed user attempts every protected API action. Users **without** the required permission must get **403** (**SECURE**); **2xx** is a **BREACH**. Users **with** permission are checked too (**ALLOW_OK** if not 403). The script bootstraps all fixture data in the database first — **no SKIP**.

### Prerequisites

```bash
docker compose up -d postgres
cd backend && alembic upgrade head
python scripts/seed_rbac_users.py
# Start API (seeds demo data on first boot)
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Seed users: `rbac-{NN}-{slug}@seed.local`, password `SeedUser123!` (or `SEED_USER_PASSWORD`). Full list: [`backend/seed-output/rbac-users.md`](../backend/seed-output/rbac-users.md).

### Run

```bash
cd backend
python3 scripts/rbac_breach_probe.py --base-url http://127.0.0.1:8000
```

By default the script mints a **Bearer JWT per seed user from the database** (same token the API validates) so the full matrix runs in a few minutes without login rate limits. Use `--http-login` to exercise cookie login via `POST /api/v1/auth/login` instead (~10–12 minutes for 50 users with `--login-delay 13`).

Options:

- `--users 11,9,5` — probe only selected seed indices (faster spot checks)
- `--http-login` — authenticate through the login endpoint (respects `--login-delay`)
- `--login-delay 13` — pause between logins when using `--http-login` (auth rate limit is 5/minute)
- `--output seed-output/rbac-breach-report.md` — markdown report (CSV written alongside)

### Report

Output: [`backend/seed-output/rbac-breach-report.md`](../backend/seed-output/rbac-breach-report.md) and `.csv` with columns: user, role, probe, mode (negative/positive), required permission, HTTP status, **SECURE** / **BREACH** / **ALLOW_OK** / **DENY_UNEXPECTED** / **FAIL**.
