import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import aircraft, work_orders

APP_ENV = os.getenv("APP_ENV", "development")

DESCRIPTION = """
**MaintainX Demo API** — a portfolio sample of an aircraft maintenance work
order service, modeled on DoD / Air Force depot operations.

* `Aircraft` — tail number, model, squadron, operational status
* `WorkOrder` — priority, assignment, status (with a validated state machine)

Designed to be exercised by both PyTest (unit/integration) and Playwright
(end-to-end API), so the same business rules are verified by two independent
test stacks.
""".strip()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="MaintainX Demo API",
    version="1.0.0",
    description=DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://demo.seethedemo.site",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(aircraft.router)
app.include_router(work_orders.router)


@app.get("/", tags=["meta"])
async def root():
    return {"status": "ok", "service": "MaintainX Demo API"}


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "healthy", "environment": APP_ENV}
