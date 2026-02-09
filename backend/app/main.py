from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import Base, engine, SessionLocal
from app.api.routes_facilities import router as facilities_router
from app.api.routes_patients import router as patients_router
from app.api.routes_agent import router as agent_router
from app.api.routes_checkin import router as checkin_router
from app.seed.seed_data import seed_if_empty


app = FastAPI(title="AI-Fest Prototype Backend", version="0.1.0")

# CORS for local frontend dev (tighten later if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed if empty
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/")
def health():
    return {"status": "ok"}


app.include_router(facilities_router)
app.include_router(patients_router)
app.include_router(agent_router)
app.include_router(checkin_router)  # check-in router