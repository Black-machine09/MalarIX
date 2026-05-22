from fastapi import FastAPI
from fastapi import status
from fastapi.responses import JSONResponse


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

    def _abs_model_path() -> str:
        try:
            return str(settings.model_path.resolve())
        except Exception:
            return str(settings.model_path)

    @app.on_event("startup")
    async def _startup_check_model() -> None:
        # Only validate existence in non-demo mode.
        if not settings.demo_mode:
            model_path = settings.model_path
            if (not model_path.exists()) or (not model_path.is_file()):
                # Raising here makes startup fail fast, and the error is visible in logs.
                raise RuntimeError(
                    "ONNX model file is missing on startup. "
                    f"model_path={model_path} "
                    f"model_path_abs={_abs_model_path()} "
                    f"exists={model_path.exists()} is_file={model_path.is_file()} "
                    "hint=Ensure model/malaria_resnet18.onnx is included in the deployment image, "
                    "or set DEMO_MODE=true."
                )


    app.include_router(health_router)
    app.include_router(predict_router)
    app.include_router(stats_router)
    app.include_router(occurrences_router)
    return app



app = create_app()

