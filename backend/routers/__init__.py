from backend.routers.analysis import router as analysis_router
from backend.routers.auth import router as auth_router
from backend.routers.demo import router as demo_router
from backend.routers.exports import router as export_router
from backend.routers.tenders import router as tender_router

__all__ = ["auth_router", "tender_router", "analysis_router", "export_router", "demo_router"]
