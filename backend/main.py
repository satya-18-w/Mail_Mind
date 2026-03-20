"""FastAPI application entry point."""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.api.email_routes import router as email_router
from backend.api.auth_routes import router as auth_router
from backend.core.config import get_settings
from backend.database.session import engine, Base


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.auto_create_tables:
        try:
            async def _create_tables() -> None:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)

            await asyncio.wait_for(
                _create_tables(),
                timeout=max(1, settings.db_init_timeout_seconds),
            )
        except TimeoutError:
            logger.exception("Database initialization timed out during startup")
        except Exception:
            logger.exception("Database initialization failed during startup")
    yield


app = FastAPI(
    title="AI Mail Intelligence Agent",
    description="Multi-agent AI email classification and priority system",
    version="2.0.0",
    lifespan=lifespan,
)

settings = get_settings()

allowed_origins = ["https://mail-mind-six.vercel.app"]
if settings.frontend_url and settings.frontend_url not in allowed_origins:
    allowed_origins.append(settings.frontend_url)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"service": "ai-mail-agent", "status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
