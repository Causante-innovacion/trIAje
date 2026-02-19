"""
GPT Legal - Main FastAPI Application
Pre-evaluación jurídica para organizaciones civiles
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.features.intake.router import router as intake_router
from app.features.evaluation.router import router as evaluation_router
from app.features.query.router import router as query_router
from app.features.advisor_prep.router import router as advisor_prep_router
from app.features.legal_adviser.router import router as legal_adviser_router
from app.features.compliance.router import router as compliance_router
from app.features.documents.router import router as documents_router
from app.features.chat.router import router as chat_router
from app.modules.rag import initialize_rag, shutdown_rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print(f"Starting GPT Legal API v{settings.VERSION}")

    # Initialize RAG module with Qdrant
    try:
        rag_module = await initialize_rag()
        print(f"RAG module initialized (Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT})")
    except Exception as e:
        print(f"Warning: Could not initialize RAG module: {e}")

    yield

    # Shutdown
    print("Shutting down GPT Legal API")
    await shutdown_rag()


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
app.include_router(intake_router, prefix="/api/v1/intake", tags=["Intake"])
app.include_router(evaluation_router, prefix="/api/v1/evaluation", tags=["Evaluación"])
app.include_router(query_router, prefix="/api/v1/query", tags=["Consultas"])
app.include_router(advisor_prep_router, prefix="/api/v1/advisor-prep", tags=["Preparar Asesor"])
app.include_router(legal_adviser_router, prefix="/api/v1/legal-adviser", tags=["Asesor Legal"])
app.include_router(compliance_router, prefix="/api/v1/compliance", tags=["Cumplimiento"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documentos RAG"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])


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
        "intake": "/api/v1/intake",
        "documents": "/api/v1/documents",
        "tools": [
            {"id": "evaluation", "name": "Evaluación Legal", "endpoint": "/api/v1/evaluation"},
            {"id": "compliance", "name": "Ruta de Cumplimiento", "endpoint": "/api/v1/compliance"},
            {"id": "query", "name": "Consulta Legal", "endpoint": "/api/v1/query"},
            {"id": "chat", "name": "Chat Inteligente", "endpoint": "/api/v1/chat"},
        ],
        "rag": {
            "status": "/api/v1/documents/status",
            "search": "/api/v1/documents/search",
            "upload": "/api/v1/documents/upload",
        }
    }
