import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.database.base import Base
from backend.database.session import engine
from backend.middleware.error_handlers import register_exception_handlers
from backend.routers import analysis_router, auth_router, demo_router, export_router, tender_router
from backend.utils.file_utils import ensure_directories

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(
    title=settings.app_name,
    description="AI-powered tender analysis platform with OCR, BOQ analytics, risk detection, and exports.",
    version="1.0.0",
    contact={"name": "AI Tender Platform"},
    swagger_ui_parameters={"docExpansion": "none", "displayRequestDuration": True},
    openapi_tags=[
        {"name": "Authentication", "description": "User registration and JWT login"},
        {"name": "Tenders", "description": "Tender uploads and retrieval"},
        {"name": "Analysis", "description": "Clause, BOQ, and risk extraction"},
        {"name": "Export", "description": "PDF and Excel report generation"},
        {"name": "Demo", "description": "Demo data and sample output generation"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)


@app.on_event("startup")
def startup():
    ensure_directories(settings.uploads_dir, settings.reports_dir)
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(tender_router)
app.include_router(analysis_router)
app.include_router(export_router)
app.include_router(demo_router)


@app.get("/health")
def health():
    return {"status": "ok"}
