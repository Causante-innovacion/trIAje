"""
Script de procesamiento ETL para documentos legales
Convierte PDFs en chunks vectorizados y los carga a ChromaDB
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import argparse

# Dependencias instaladas en requirements.txt
# Si falta alguna: pip install -r requirements.txt

from llama_parse import LlamaParse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Configuración - Rutas absolutas
BASE_DIR = Path(__file__).parent.parent.parent  # Raíz del proyecto
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base"
METADATA_PATH = KNOWLEDGE_BASE_PATH / "metadata"
CHROMA_DB_PATH = BASE_DIR / "chroma_db"


class DocumentProcessor:
    """Procesador de documentos legales para RAG"""
    
    def __init__(self, llama_api_key: str = None):
        """
        Args:
            llama_api_key: API key para llama-parse (obtener en https://cloud.llamaindex.ai)
        """
        # Cargar variables de entorno
        from dotenv import load_dotenv
        load_dotenv()
        
        # Inicializar parser de PDFs
        self.parser = LlamaParse(
            api_key=llama_api_key or os.getenv("LLAMA_CLOUD_API_KEY"),
            result_type="markdown",  # Mejor para PDFs complejos
            language="es",
            verbose=True
        )
        
        # Inicializar chunker
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        
        # Inicializar embeddings (modelo gratuito multilingüe)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
    def load_metadata(self, doc_id: str) -> Dict:
        """Carga metadata de un documento desde JSON"""
        metadata_file = METADATA_PATH / f"{doc_id}.json"
        
        if not metadata_file.exists():
            print(f"⚠️  Advertencia: No se encontró metadata para {doc_id}")
            return {
                "doc_id": doc_id,
                "tipo": "desconocido",
                "categoria": "general"
            }
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_pdf(self, pdf_path: Path) -> str:
        """Extrae texto de PDF usando llama-parse"""
        print(f"📄 Procesando: {pdf_path.name}")
        
        try:
            documents = self.parser.load_data(str(pdf_path))
            # Concatenar todo el texto
            full_text = "\n\n".join([doc.text for doc in documents])
            return full_text
        except Exception as e:
            print(f"❌ Error al procesar {pdf_path.name}: {e}")
            return ""
    
    def create_chunks(self, text: str, metadata: Dict) -> List[Document]:
        """Divide texto en chunks y agrega metadata"""
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            # Crear documento con metadata completa
            doc_metadata = {
                **metadata,  # Metadata del JSON
                "chunk_id": i,
                "chunk_total": len(chunks)
            }
            
            documents.append(Document(
                page_content=chunk,
                metadata=doc_metadata
            ))
        
        print(f"   ✂️  Creados {len(chunks)} chunks")
        return documents
    
    def process_document(self, pdf_path: Path, doc_id: str = None) -> List[Document]:
        """Procesa un PDF completo: parse → chunk → metadata"""
        
        # Inferir doc_id del nombre del archivo si no se proporciona
        if not doc_id:
            doc_id = pdf_path.stem
        
        # 1. Cargar metadata
        metadata = self.load_metadata(doc_id)
        
        # 2. Parsear PDF
        text = self.parse_pdf(pdf_path)
        if not text:
            return []
        
        # 3. Crear chunks con metadata
        documents = self.create_chunks(text, metadata)
        
        return documents
    
    def process_category(self, category: str) -> List[Document]:
        """Procesa todos los documentos de una categoría"""
        category_path = KNOWLEDGE_BASE_PATH / "normas" / category
        
        if not category_path.exists():
            print(f"❌ Categoría no encontrada: {category}")
            return []
        
        all_documents = []
        pdf_files = list(category_path.glob("*.pdf"))
        
        print(f"\n📚 Procesando categoría: {category.upper()}")
        print(f"   Documentos encontrados: {len(pdf_files)}\n")
        
        for pdf_file in pdf_files:
            docs = self.process_document(pdf_file)
            all_documents.extend(docs)
        
        return all_documents
    
    def load_to_vectorstore(self, documents: List[Document], collection_name: str = "leyes_peru"):
        """Carga documentos a ChromaDB"""
        print(f"\n🧠 Cargando {len(documents)} chunks a ChromaDB...")
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(CHROMA_DB_PATH),
            collection_name=collection_name
        )
        
        print(f"✅ Carga completada a colección '{collection_name}'")
        return vectorstore


def main():
    parser = argparse.ArgumentParser(description="Procesar documentos legales para RAG")
    parser.add_argument("--all", action="store_true", help="Procesar todos los documentos")
    parser.add_argument("--category", type=str, help="Procesar solo una categoría (sunat, apci, etc.)")
    parser.add_argument("--doc", type=str, help="Procesar un documento específico por doc_id")
    parser.add_argument("--api-key", type=str, help="API key de llama-parse")
    
    args = parser.parse_args()
    
    # Inicializar procesador
    processor = DocumentProcessor(llama_api_key=args.api_key)
    
    all_documents = []
    
    if args.all:
        # Procesar todas las categorías
        categories = ["sunat", "apci", "civil", "laboral", "pi"]
        for cat in categories:
            docs = processor.process_category(cat)
            all_documents.extend(docs)
    
    elif args.category:
        # Procesar categoría específica
        docs = processor.process_category(args.category)
        all_documents.extend(docs)
    
    elif args.doc:
        # Procesar documento específico
        # Buscar el PDF correspondiente
        for pdf_path in KNOWLEDGE_BASE_PATH.rglob("*.pdf"):
            if pdf_path.stem == args.doc or args.doc in pdf_path.stem:
                docs = processor.process_document(pdf_path, args.doc)
                all_documents.extend(docs)
                break
        else:
            print(f"❌ No se encontró documento con ID: {args.doc}")
            return
    
    else:
        print("⚠️  Especifica --all, --category o --doc")
        return
    
    # Cargar a base vectorial
    if all_documents:
        processor.load_to_vectorstore(all_documents)
        
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        print(f"Total de chunks procesados: {len(all_documents)}")
        print(f"Ubicación ChromaDB: {CHROMA_DB_PATH}")
        print("\n✅ Proceso completado exitosamente!")
    else:
        print("\n⚠️  No se procesaron documentos")


if __name__ == "__main__":
    main()
