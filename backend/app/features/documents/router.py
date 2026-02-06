"""
Documents Feature - Router
Endpoints para gestión de documentos y RAG.
"""

from fastapi import APIRouter, HTTPException

from .schemas import (
    DocumentUploadRequest,
    DocumentUploadResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    RAGStatusResponse,
)
from .service import document_service

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(request: DocumentUploadRequest):
    """
    Sube un documento al sistema RAG.

    El documento se procesa en chunks y se genera embeddings para búsqueda semántica.

    - Para normativa compartida: no especificar organization_id
    - Para docs privados de org: especificar organization_id

    Args:
        request: DocumentUploadRequest con el documento y metadata

    Returns:
        DocumentUploadResponse con info del documento indexado
    """
    try:
        return await document_service.upload_document(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo documento: {str(e)}")


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(request: DocumentSearchRequest):
    """
    Busca documentos usando RAG.

    Realiza búsqueda semántica en las colecciones de ChromaDB.

    - Si se especifica organization_id: busca en normativa + docs de la org
    - Sin organization_id: busca solo en normativa compartida

    Args:
        request: DocumentSearchRequest con la consulta

    Returns:
        DocumentSearchResponse con los chunks más relevantes
    """
    try:
        return await document_service.search_documents(request)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")


@router.get("/status", response_model=RAGStatusResponse)
async def get_rag_status():
    """
    Obtiene el estado del sistema RAG.

    Retorna información sobre:
    - Salud del sistema
    - Modo de ChromaDB (local, server, memory)
    - Colecciones disponibles y estadísticas

    Returns:
        RAGStatusResponse con el estado actual
    """
    try:
        return await document_service.get_rag_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """
    Elimina un documento por su ID.

    Elimina todos los chunks asociados al documento de todas las colecciones.

    Args:
        doc_id: ID del documento a eliminar

    Returns:
        Mensaje de confirmación
    """
    try:
        deleted = await document_service.delete_document(doc_id)
        if deleted:
            return {"message": f"Documento {doc_id} eliminado"}
        else:
            raise HTTPException(status_code=404, detail=f"Documento {doc_id} no encontrado")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando documento: {str(e)}")


@router.get("/collections")
async def list_collections():
    """
    Lista las colecciones disponibles en ChromaDB.

    Returns:
        Lista de nombres de colecciones
    """
    try:
        from app.modules.rag import get_rag_module, ChromaDBAdapter

        rag = get_rag_module()
        if not isinstance(rag.vector_store, ChromaDBAdapter):
            raise RuntimeError("Vector store no es ChromaDB")

        collections = await rag.vector_store.list_indices()
        return {"collections": collections}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando colecciones: {str(e)}")


@router.get("/collections/{collection_name}/stats")
async def get_collection_stats(collection_name: str):
    """
    Obtiene estadísticas de una colección específica.

    Args:
        collection_name: Nombre de la colección

    Returns:
        Estadísticas de la colección
    """
    try:
        from app.modules.rag import get_rag_module, ChromaDBAdapter

        rag = get_rag_module()
        if not isinstance(rag.vector_store, ChromaDBAdapter):
            raise RuntimeError("Vector store no es ChromaDB")

        stats = await rag.vector_store.get_index_stats(collection_name)
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])

        return stats
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo stats: {str(e)}")
