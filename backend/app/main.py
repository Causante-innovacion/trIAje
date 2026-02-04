"""
GPT Legal - Main FastAPI Application
Pre-evaluación jurídica para organizaciones civiles
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.features.evaluation.router import router as evaluation_router
from app.features.query.router import router as query_router
from app.features.advisor_prep.router import router as advisor_prep_router
from app.features.compliance.router import router as compliance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print(f"Starting GPT Legal API v{settings.VERSION}")
    yield
    # Shutdown
    print("Shutting down GPT Legal API")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Herramienta de pre-evaluación jurídica para organizaciones civiles",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(evaluation_router, prefix="/api/v1/evaluation", tags=["Evaluación"])
app.include_router(query_router, prefix="/api/v1/query", tags=["Consultas"])
app.include_router(advisor_prep_router, prefix="/api/v1/advisor-prep", tags=["Preparar Asesor"])
app.include_router(compliance_router, prefix="/api/v1/compliance", tags=["Cumplimiento"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "modes": [
            {"id": 1, "name": "Evaluar proyecto", "endpoint": "/api/v1/evaluation"},
            {"id": 2, "name": "Duda puntual", "endpoint": "/api/v1/query"},
            {"id": 3, "name": "Preparar reunión con asesor", "endpoint": "/api/v1/advisor-prep"},
            {"id": 4, "name": "Ruta de cumplimiento", "endpoint": "/api/v1/compliance"},
        ]
    }
