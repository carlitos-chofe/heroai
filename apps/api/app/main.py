import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.health import router as health_router
from app.api.routes.profiles import router as profiles_router
from app.api.routes.stories import router as stories_router
from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure storage directory exists at startup
    storage_dir = Path(settings.local_asset_dir) / "stories"
    storage_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Storage directory ready: {storage_dir}")
    yield
    logger.info("Shutting down Hero AI API")


app = FastAPI(
    title="Hero Adventure AI API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static asset serving: /assets → LOCAL_ASSET_DIR
assets_dir = Path(settings.local_asset_dir)
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
else:
    logger.warning(f"Assets directory does not exist yet: {assets_dir} (will be created on first story)")


# Global exception handler for clean error format
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": {"code": "internal_error", "message": "Internal server error"}},
    )


# Routers
app.include_router(health_router)
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(stories_router, prefix="/api/v1")
