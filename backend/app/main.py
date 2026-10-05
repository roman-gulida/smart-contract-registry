"""
Smart Contract Document Registry - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.api.routes import router
from app.core.config import settings
from app.services.storage_service import get_storage_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Ensure the S3 bucket exists in SeaweedFS
    storage = get_storage_service()
    storage.ensure_bucket()
    yield


app = FastAPI(
    title="Smart Contract Document Registry API",
    description="Upload PDFs, classify with ML, store on blockchain",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
