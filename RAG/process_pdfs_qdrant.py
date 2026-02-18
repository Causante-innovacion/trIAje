"""
Script para procesar PDFs y cargarlos a Qdrant (base de datos vectorial remota)

Uso:
    python process_pdfs_qdrant.py              # Procesa todos los PDFs
    python process_pdfs_qdrant.py --dry-run    # Solo muestra qué procesaría
"""

import os
import json
import sys
import io
from pathlib import Path
from typing import List, Dict

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base"
NORMAS_PATH = KNOWLEDGE_BASE_PATH / "normas"
TAGS_FILE = BASE_DIR / "document_tags.json"

# Configuración de Qdrant
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "legal_documents"


def load_document_tags() -> Dict:
    """Carga el archivo de configuración de etiquetas"""
    if not TAGS_FILE.exists():
        print(f"❌ No se encontró {TAGS_FILE}")
        return {}
    
    with open(TAGS_FILE, 'r', encoding='utf-8') as f:
        tags = json.load(f)
    
    # Filtrar comentarios (keys que empiezan con _)
    return {k: v for k, v in tags.items() if not k.startswith('_')}


def find_all_pdfs() -> List[Path]:
    """Encuentra todos los PDFs en knowledge_base/normas/"""
    pdfs = []
    for folder in NORMAS_PATH.iterdir():
        if folder.is_dir():
            pdfs.extend(folder.glob("*.pdf"))
    return sorted(pdfs)


def extract_text_pymupdf(pdf_path: Path) -> str:
    """Extrae texto de PDF usando PyMuPDF"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("  ❌ PyMuPDF no instalado. Ejecuta: pip install PyMuPDF")
        return ""

    try:
        doc = fitz.open(str(pdf_path))
        text_parts = []
        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                text_parts.append(f"--- Página {page_num + 1} ---\n{text}")
        doc.close()

        full_text = "\n\n".join(text_parts)
        print(f"  📄 Extraídas {len(text_parts)} páginas ({len(full_text):,} caracteres)")
        return full_text
    except Exception as e:
        print(f"  ❌ Error al procesar {pdf_path.name}: {e}")
        return ""


def create_chunks(text: str, metadata: Dict) -> list:
    """Divide texto en chunks con metadata"""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )

    chunks = splitter.split_text(text)
    
    documents = []
    for i, chunk in enumerate(chunks):
        doc_metadata = {
            **metadata,
            "chunk_id": i,
            "chunk_total": len(chunks),
            "text": chunk  # Qdrant necesita el texto en metadata también
        }
        documents.append(doc_metadata)

    print(f"  ✂️  Creados {len(chunks)} chunks")
    return documents, [chunk for chunk in chunks]


def load_to_qdrant(documents: list, texts: list):
    """Carga documentos a Qdrant remoto"""
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    from sentence_transformers import SentenceTransformer
    import time
    
    print(f"\n🔌 Conectando a Qdrant ({QDRANT_HOST}:{QDRANT_PORT})...")
    
    try:
        # Aumentar timeout a 120 segundos
        client = QdrantClient(
            host=QDRANT_HOST, 
            port=QDRANT_PORT,
            timeout=120  # 2 minutos de timeout
        )
        
        # Verificar conexión
        collections = client.get_collections()
        print(f"✅ Conexión exitosa a Qdrant")
        print(f"   Colecciones existentes: {len(collections.collections)}")
        
    except Exception as e:
        print(f"❌ Error al conectar con Qdrant: {e}")
        print(f"\n💡 Asegúrate de que:")
        print(f"   1. El túnel SSH está activo: ssh -L 6333:localhost:6333 debian@142.44.241.25")
        print(f"   2. Qdrant está corriendo en el servidor en puerto 6333")
        raise

    # Cargar modelo de embeddings
    print(f"\n🧠 Cargando modelo de embeddings...")
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    vector_size = 768  # Tamaño del modelo paraphrase-multilingual-mpnet-base-v2
    
    # Crear o recrear colección
    try:
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"🗑️  Colección '{COLLECTION_NAME}' eliminada (recreando limpia)")
    except:
        pass
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    print(f"📂 Colección '{COLLECTION_NAME}' creada")

    # Generar embeddings
    print(f"\n🔢 Generando embeddings para {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    # Preparar puntos para Qdrant
    print(f"\n📥 Cargando chunks a Qdrant...")
    points = []
    for idx, (embedding, metadata) in enumerate(zip(embeddings, documents)):
        point = PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload=metadata
        )
        points.append(point)
    
    # Cargar en lotes más pequeños con reintentos
    batch_size = 20  # Reducido de 100 a 20 para evitar timeouts
    max_retries = 3
    
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        batch_num = i//batch_size + 1
        total_batches = (len(points)-1)//batch_size + 1
        
        # Intentar con reintentos
        for attempt in range(max_retries):
            try:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=batch
                )
                print(f"  ✅ Lote {batch_num}/{total_batches} cargado ({len(batch)} chunks)")
                break  # Éxito, salir del loop de reintentos
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                    print(f"  ⚠️  Lote {batch_num} falló (intento {attempt + 1}/{max_retries}). Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ Lote {batch_num} falló después de {max_retries} intentos: {e}")
                    raise

    # Verificar
    collection_info = client.get_collection(collection_name=COLLECTION_NAME)
    print(f"\n✅ Carga completada. Total puntos en colección: {collection_info.points_count:,}")


def process_pdfs(dry_run: bool = False):
    """Procesa todos los PDFs con sus etiquetas"""
    
    # Cargar configuración de etiquetas
    document_tags = load_document_tags()
    if not document_tags:
        print("❌ No hay configuración de etiquetas")
        return
    
    # Encontrar todos los PDFs
    all_pdfs = find_all_pdfs()
    print(f"\n📚 Encontrados {len(all_pdfs)} PDFs en knowledge_base/normas/")
    
    all_documents = []
    all_texts = []
    processed = 0
    skipped = 0
    failed = 0

    for pdf_path in all_pdfs:
        filename = pdf_path.name
        
        print(f"\n{'='*60}")
        print(f"📄 Procesando: {filename}")
        print(f"   Ruta: {pdf_path.relative_to(NORMAS_PATH)}")
        print(f"{'='*60}")

        # Obtener etiquetas del archivo
        tags = document_tags.get(filename)
        
        if not tags:
            print(f"  ⚠️  No hay etiquetas configuradas para este PDF - OMITIDO")
            skipped += 1
            continue

        # Preparar metadata
        metadata = {
            "source": filename,
            "intenciones": ", ".join(tags.get("intenciones", [])),  # String para Qdrant
            "tipo_fuente": tags.get("tipo", "complementario"),
            "categoria": tags.get("categoria", "general"),
        }

        print(f"  🏷️  Intenciones: {metadata['intenciones']}")
        print(f"  📂 Categoría: {metadata['categoria']}")
        print(f"  📌 Tipo: {metadata['tipo_fuente']}")

        if dry_run:
            processed += 1
            continue

        # Extraer texto
        text = extract_text_pymupdf(pdf_path)
        
        if not text:
            print(f"  ⚠️  No se pudo extraer texto")
            failed += 1
            continue

        # Crear chunks
        chunks_metadata, chunks_text = create_chunks(text, metadata)
        all_documents.extend(chunks_metadata)
        all_texts.extend(chunks_text)
        processed += 1

    # Resumen
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DE PROCESAMIENTO")
    print(f"{'='*60}")
    print(f"  PDFs encontrados: {len(all_pdfs)}")
    print(f"  Procesados: {processed}")
    print(f"  Omitidos (sin etiquetas): {skipped}")
    print(f"  Fallidos: {failed}")
    print(f"  Total chunks creados: {len(all_documents):,}")

    if dry_run:
        print(f"\n🔍 Modo dry-run - No se cargaron documentos a Qdrant")
        return

    if all_documents:
        load_to_qdrant(all_documents, all_texts)
    else:
        print("\n⚠️  No hay documentos para cargar")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Procesar PDFs con etiquetas de intención para Qdrant")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar qué se procesaría")
    args = parser.parse_args()

    print("\n🚀 PROCESAMIENTO DE PDFs CON QDRANT")
    print("="*60)
    
    process_pdfs(dry_run=args.dry_run)
    
    print("\n✅ Proceso completado!")
    print(f"\n💡 Dashboard de Qdrant: http://localhost:6333/dashboard")


if __name__ == "__main__":
    main()
