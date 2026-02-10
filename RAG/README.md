# RAG - Base de Conocimiento Legal

Modulo de Retrieval Augmented Generation (RAG) del proyecto GPT Legal.
Contiene la base de conocimiento legal (PDFs + respuestas modelo) y la base vectorial ChromaDB.

**No es un proyecto independiente.** Las dependencias se instalan desde `backend/requirements.txt`.

## Estructura

```
RAG/
├── chroma_db/              # Base vectorial ChromaDB (generada por ETL)
├── knowledge_base/
│   ├── intenciones/        # Respuestas modelo por intencion legal (archivos .md)
│   ├── metadata/           # JSON metadata de cada PDF procesado
│   ├── normas/             # PDFs legales organizados por categoria
│   │   ├── civil/
│   │   ├── compliance/
│   │   ├── cooperacion/
│   │   ├── laboral/
│   │   ├── propiedad_intelectual/
│   │   └── tributario/
│   ├── documentacion/
│   ├── preguntas/
│   └── procedimientos/
├── docs/                   # Documentacion del sistema RAG
├── rag_demo.py             # Demo: RAG completo (ChromaDB + GPT)
├── test_busqueda.py        # Test: busqueda semantica en ChromaDB
├── process_new_documents.py # ETL: procesar PDFs nuevos con PyMuPDF
└── etl_llamaparse.py       # ETL alternativo con LlamaParse (API)
```

## Uso

Todos los scripts se ejecutan desde el venv del backend:

```powershell
# Desde la raiz del proyecto
cd backend
.\venv\Scripts\Activate.ps1

# Probar busqueda semantica
python ../RAG/test_busqueda.py

# Probar RAG completo (requiere OPENAI_API_KEY en RAG/.env)
python ../RAG/rag_demo.py

# Procesar nuevos PDFs y cargar a ChromaDB
python ../RAG/process_new_documents.py
python ../RAG/process_new_documents.py --dry-run
python ../RAG/process_new_documents.py --category cooperacion
```

## ChromaDB

- **Coleccion**: `leyes_peru`
- **Embeddings**: HuggingFace `paraphrase-multilingual-mpnet-base-v2` (768 dims)
- **Chunks**: ~2,494 (de ~20 PDFs legales peruanos)

El backend se conecta a esta misma base vectorial via `CHROMA_PERSIST_DIR=../RAG/chroma_db`.

## Agregar nuevos documentos

1. Colocar el PDF en `knowledge_base/normas/<categoria>/`
2. Crear metadata JSON en `knowledge_base/metadata/` (ver TEMPLATE.json)
3. Ejecutar `python ../RAG/process_new_documents.py --doc nombre_documento`
