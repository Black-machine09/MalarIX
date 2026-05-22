from fastapi import FastAPI

# Load environment variables from .env (if python-dotenv is installed).
# This keeps local dev simple while still allowing real env vars in production.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


from fastapi.middleware.cors import CORSMiddleware

from api.routes.health import router as health_router
from api.routes.predict import router as predict_router
from api.routes.stats import router as stats_router
from api.routes.occurrences import router as occurrences_router
from core.config import get_settings
from core.logger import configure_logging



def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.model_version,
        description=(
            "AI-assisted malaria screening triage prototype. "
            "Not a medical diagnostic device."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(predict_router)
    app.include_router(stats_router)
    app.include_router(occurrences_router)
    return app


app = create_app()

