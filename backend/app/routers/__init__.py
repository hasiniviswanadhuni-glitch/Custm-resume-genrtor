from backend.app.routers.profile import router as profile_router
from backend.app.routers.job import router as job_router
from backend.app.routers.match import router as match_router
from backend.app.routers.suggestions import router as suggestions_router
from backend.app.routers.resume import router as resume_router
from backend.app.routers.export import router as export_router

__all__ = [
    "profile_router",
    "job_router",
    "match_router",
    "suggestions_router",
    "resume_router",
    "export_router",
]
