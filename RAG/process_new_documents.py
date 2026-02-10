"""
Script para procesar los nuevos documentos legales de 'Documentos LEGALES'
y agregarlos a la base vectorial ChromaDB existente.

Soporta dos modos de extracción:
1. LlamaParse (mejor calidad, requiere API key) - DEFAULT si hay API key
2. PyMuPDF/fitz (gratuito, buena calidad) - FALLBACK si no hay API key

Uso:
    python process_new_documents.py              # Procesa todos los nuevos PDFs
    python process_new_documents.py --category cooperacion  # Solo una categoría
    python process_new_documents.py --dry-run     # Solo muestra qué procesaría
"""

import os
import json
import sys
import io
from pathlib import Path
from typing import List, Dict

# Fix Windows console encoding for emojis/unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base"
METADATA_PATH = KNOWLEDGE_BASE_PATH / "metadata"
CHROMA_DB_PATH = BASE_DIR / "chroma_db"
NORMAS_PATH = KNOWLEDGE_BASE_PATH / "normas"

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Nuevos documentos a procesar (doc_id → path relativo desde normas/)
NEW_DOCUMENTS = {
    # Cooperación Internacional (APCI)
    "ley_27692_apci": "cooperacion/ley_27692_apci.pdf",
    "ds_032_2025_reglamento_apci": "cooperacion/ds_032_2025_reglamento_apci.pdf",
    "resolucion_00774_apci": "cooperacion/resolucion_00774_apci.pdf",
    "resolucion_00821_apci": "cooperacion/resolucion_00821_apci.pdf",
    "dl_816": "cooperacion/dl_816.pdf",
    "ley_31324": "cooperacion/ley_31324.pdf",
    # Protección de Datos
    "ley_29733_datos_personales": "propiedad_intelectual/ley_29733_datos_personales.pdf",
    "ds_003_2013_reglamento_datos_personales": "propiedad_intelectual/ds_003_2013_reglamento_datos_personales.pdf",
    # Tributario
    "ds_122_reglamento_lir": "tributario/ds_122_reglamento_lir.pdf",
    "ley_ruc": "tributario/ley_ruc.pdf",
    "capitulo_i_ruc": "tributario/capitulo_i_ruc.pdf",
    # Laboral
    "dl_728_productividad_laboral": "laboral/dl_728_productividad_laboral.pdf",
    "ley_25897_cts": "laboral/ley_25897_cts.pdf",
    "ley_26790_seguridad_social": "laboral/ley_26790_seguridad_social.pdf",
    "ley_28238_voluntariado": "laboral/ley_28238_voluntariado.pdf",
    "ds_003_2015_reglamento_voluntariado": "laboral/ds_003_2015_reglamento_voluntariado.pdf",
    "dl_1350_migraciones": "laboral/dl_1350_migraciones.pdf",
}

# Categorías y sus documentos
CATEGORIES = {
    "cooperacion": [
        "ley_27692_apci", "ds_032_2025_reglamento_apci",
        "resolucion_00774_apci", "resolucion_00821_apci",
        "dl_816", "ley_31324"
    ],
    "propiedad_intelectual": [
        "ley_29733_datos_personales", "ds_003_2013_reglamento_datos_personales"
    ],
    "tributario": [
        "ds_122_reglamento_lir", "ley_ruc", "capitulo_i_ruc"
    ],
    "laboral": [
        "dl_728_productividad_laboral", "ley_25897_cts",
        "ley_26790_seguridad_social", "ley_28238_voluntariado",
        "ds_003_2015_reglamento_voluntariado", "dl_1350_migraciones"
    ],
}


def load_metadata(doc_id: str) -> Dict:
    """Carga metadata de un documento desde su JSON"""
    # Buscar archivos de metadata que contengan el doc_id
    for meta_file in METADATA_PATH.glob("*.json"):
        if meta_file.name == "TEMPLATE.json":
            continue
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("doc_id") == doc_id:
                    return data
        except (json.JSONDecodeError, KeyError):
            continue

    print(f"  ⚠️  No se encontró metadata para '{doc_id}', usando valores por defecto")
    return {"doc_id": doc_id, "tipo": "norma", "categoria": "general"}


def extract_text_pymupdf(pdf_path: Path) -> str:
    """Extrae texto de PDF usando PyMuPDF (fitz) - gratuito"""
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
        print(f"  📄 Extraídas {len(text_parts)} páginas ({len(full_text)} caracteres)")
        return full_text
    except Exception as e:
        print(f"  ❌ Error al procesar {pdf_path.name}: {e}")
        return ""


def extract_text_llamaparse(pdf_path: Path, api_key: str) -> str:
    """Extrae texto de PDF usando LlamaParse (mejor calidad)"""
    try:
        from llama_parse import LlamaParse
    except ImportError:
        print("  ❌ llama-parse no instalado. Ejecuta: pip install llama-parse")
        return ""

    try:
        parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",
            language="es",
            verbose=False
        )
        documents = parser.load_data(str(pdf_path))
        full_text = "\n\n".join([doc.text for doc in documents])
        print(f"  📄 Extraídas {len(documents)} secciones ({len(full_text)} caracteres)")
        return full_text
    except Exception as e:
        print(f"  ❌ Error con LlamaParse en {pdf_path.name}: {e}")
        return ""


def create_chunks(text: str, metadata: Dict) -> list:
    """Divide texto en chunks y agrega metadata"""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document

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
            "chunk_total": len(chunks)
        }
        # Limpiar metadata: solo strings, ints, floats, bools
        clean_metadata = {}
        for k, v in doc_metadata.items():
            if isinstance(v, (str, int, float, bool)):
                clean_metadata[k] = v
            elif isinstance(v, list):
                clean_metadata[k] = ", ".join(str(x) for x in v)
            elif v is None:
                clean_metadata[k] = ""
            elif isinstance(v, dict):
                clean_metadata[k] = json.dumps(v, ensure_ascii=False)

        documents.append(Document(page_content=chunk, metadata=clean_metadata))

    print(f"  ✂️  Creados {len(chunks)} chunks")
    return documents


def load_to_chromadb(documents: list, collection_name: str = "leyes_peru"):
    """Carga documentos a la base vectorial ChromaDB existente"""
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings

    print(f"\n🧠 Cargando modelo de embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    print(f"📥 Agregando {len(documents)} chunks a ChromaDB (colección: {collection_name})...")

    vectorstore = Chroma(
        persist_directory=str(CHROMA_DB_PATH),
        embedding_function=embeddings,
        collection_name=collection_name
    )

    # Agregar documentos a la colección existente
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    vectorstore.add_texts(texts=texts, metadatas=metadatas)

    total = vectorstore._collection.count()
    print(f"✅ Carga completada. Total documentos en colección: {total}")
    return vectorstore


def process_documents(doc_ids: List[str], dry_run: bool = False):
    """Procesa una lista de documentos"""
    llama_key = os.getenv("LLAMA_CLOUD_API_KEY")
    use_llamaparse = False
    if llama_key:
        try:
            import llama_parse  # noqa: F401
            use_llamaparse = True
        except ImportError:
            pass

    if use_llamaparse:
        print("🔑 Usando LlamaParse (API key + paquete disponible)")
    else:
        print("🆓 Usando PyMuPDF (extraccion local gratuita)")

    all_documents = []
    processed = 0
    failed = 0

    for doc_id in doc_ids:
        rel_path = NEW_DOCUMENTS.get(doc_id)
        if not rel_path:
            print(f"\n❌ Doc ID no reconocido: {doc_id}")
            failed += 1
            continue

        pdf_path = NORMAS_PATH / rel_path
        if not pdf_path.exists():
            print(f"\n❌ PDF no encontrado: {pdf_path}")
            failed += 1
            continue

        print(f"\n{'='*60}")
        print(f"📄 Procesando: {doc_id}")
        print(f"   Archivo: {pdf_path.name}")
        print(f"{'='*60}")

        if dry_run:
            metadata = load_metadata(doc_id)
            print(f"  📋 Metadata: {metadata.get('titulo', 'N/A')}")
            print(f"  📂 Categoría: {metadata.get('categoria', 'N/A')}")
            print(f"  🏷️  Intenciones: {metadata.get('intenciones_aplicables', [])}")
            processed += 1
            continue

        # 1. Cargar metadata
        metadata = load_metadata(doc_id)

        # 2. Extraer texto
        if use_llamaparse:
            text = extract_text_llamaparse(pdf_path, llama_key)
        else:
            text = extract_text_pymupdf(pdf_path)

        if not text:
            print(f"  ⚠️  No se pudo extraer texto de {doc_id}")
            failed += 1
            continue

        # 3. Crear chunks
        chunks = create_chunks(text, metadata)
        all_documents.extend(chunks)
        processed += 1

    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DE PROCESAMIENTO")
    print(f"{'='*60}")
    print(f"  Procesados: {processed}")
    print(f"  Fallidos: {failed}")
    print(f"  Total chunks: {len(all_documents)}")

    if dry_run:
        print(f"\n🔍 Modo dry-run - No se cargaron documentos a ChromaDB")
        return

    if all_documents:
        load_to_chromadb(all_documents)
    else:
        print("\n⚠️  No hay documentos para cargar")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Procesar nuevos documentos legales para RAG")
    parser.add_argument("--category", type=str, help="Procesar solo una categoría")
    parser.add_argument("--doc", type=str, help="Procesar un documento específico por doc_id")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar qué se procesaría")
    parser.add_argument("--list", action="store_true", help="Listar todos los documentos disponibles")

    args = parser.parse_args()

    if args.list:
        print("\n📋 DOCUMENTOS DISPONIBLES PARA PROCESAR:")
        print("=" * 60)
        for cat, doc_ids in CATEGORIES.items():
            print(f"\n📂 {cat.upper()}:")
            for doc_id in doc_ids:
                rel_path = NEW_DOCUMENTS[doc_id]
                pdf_exists = (NORMAS_PATH / rel_path).exists()
                status = "✅" if pdf_exists else "❌"
                print(f"   {status} {doc_id}")
        return

    if args.doc:
        doc_ids = [args.doc]
    elif args.category:
        if args.category not in CATEGORIES:
            print(f"❌ Categoría no válida: {args.category}")
            print(f"   Categorías disponibles: {', '.join(CATEGORIES.keys())}")
            return
        doc_ids = CATEGORIES[args.category]
    else:
        # Procesar todos
        doc_ids = list(NEW_DOCUMENTS.keys())

    print(f"\n🚀 Procesando {len(doc_ids)} documentos...")
    process_documents(doc_ids, dry_run=args.dry_run)
    print("\n✅ Proceso completado!")


if __name__ == "__main__":
    main()
