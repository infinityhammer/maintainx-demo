# MaintainX Demo

[![Backend Tests](https://github.com/infinityhammer/maintainx-demo/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/infinityhammer/maintainx-demo/actions/workflows/backend-tests.yml)
[![Playwright E2E Tests](https://github.com/infinityhammer/maintainx-demo/actions/workflows/playwright-tests.yml/badge.svg)](https://github.com/infinityhammer/maintainx-demo/actions/workflows/playwright-tests.yml)

A portfolio demonstration of an aircraft maintenance work order system, modeled
after the kind of fleet-management tooling used in DoD / Air Force depot
operations. Built to showcase test-automation depth: a real REST API, exhaustive
PyTest coverage, parallel Playwright API coverage, an Angular UI, and a
Dockerized deployment story driven by GitHub Actions CI.

Live demo:
- API + Swagger UI: https://api.seethedemo.site/docs
- Frontend: https://demo.seethedemo.site

---

## Project Overview

The system models two core domain objects:

- **Aircraft** — an airframe with a tail number, model, squadron, and operational
  status (operational / grounded / maintenance).
- **WorkOrder** — a maintenance ticket against an aircraft, with priority,
  assignment, and a status that progresses through `open → in_progress →
  awaiting_parts → complete` (with a cancel path from any state).

The API enforces the work-order status machine — invalid transitions return
`422`. This is the kind of domain rule that distinguishes a real service from a
CRUD demo, and it is exercised by both PyTest and Playwright.

## Tech Stack

| Layer        | Stack                                                |
|--------------|------------------------------------------------------|
| Backend      | FastAPI · SQLAlchemy 2 (async) · SQLite / aiosqlite  |
| API tests    | PyTest · pytest-asyncio · httpx                      |
| E2E tests    | Playwright (TypeScript) — API + UI projects          |
| Frontend     | Angular 17 · RxJS · SCSS                             |
| Packaging    | Docker · docker-compose                              |
| CI/CD        | GitHub Actions                                       |
| Hosting      | Linode VPS · Nginx reverse proxy · Let's Encrypt     |

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm start  # serves on http://localhost:4200
```

### Full stack via Docker Compose

```bash
docker-compose up --build
```

## Running Tests

### PyTest (backend)

```bash
cd backend
pytest
```

Coverage report is printed inline; an HTML report is written to `backend/htmlcov/`.

### Playwright (E2E)

```bash
cd e2e
npm install
npx playwright install --with-deps chromium

# API project — talks to a running backend on :8000
npm run test:api

# UI project — requires the frontend on :4200 (currently a stub)
npm run test:ui
```

## Deployment

See [DEPLOY.md](./DEPLOY.md) for the full VPS deployment runbook
(`50.116.24.150` → `seethedemo.site`). Short version: clone the repo on the
VPS, `docker-compose up -d --build`, point Nginx at ports 8000 / 80, and run
`certbot` for HTTPS.

## Repository Layout

```
maintainx-demo/
├── backend/        FastAPI service + PyTest suite
├── frontend/       Angular 17 SPA
├── e2e/            Playwright tests (api + ui projects)
├── .github/        CI workflows
├── docker-compose.yml
└── DEPLOY.md
```
