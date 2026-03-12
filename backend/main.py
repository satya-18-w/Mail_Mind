"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.email_routes import router as email_router
from backend.api.auth_routes import router as auth_router
from backend.core.config import get_settings
from backend.database.session import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="AI Mail Intelligence Agent",
    description="Multi-agent AI email classification and priority system",
    version="2.0.0",
    lifespan=lifespan,
)

settings = get_settings()

allowed_origins = ["http://localhost:3000"]
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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
