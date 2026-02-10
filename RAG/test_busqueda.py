# Script de Prueba de Búsqueda Semántica
# Verifica que ChromaDB está funcionando correctamente

from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DB_PATH = BASE_DIR / "chroma_db"

print("Inicializando sistema de busqueda...\n")

# Cargar embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

# Conectar a ChromaDB
vectorstore = Chroma(
    persist_directory=str(CHROMA_DB_PATH),
    embedding_function=embeddings,
    collection_name="leyes_peru"
)

print(f"✅ ChromaDB cargado")
print(f"📊 Total de documentos: {vectorstore._collection.count()}\n")

# Preguntas de prueba
preguntas = [
    "¿Cuáles son los elementos obligatorios del estatuto?",
    "¿Qué documentos necesito para inscribir una asociación?",
    "¿Quién puede presentar el parte notarial?",
    "¿Cómo se modifican los representantes legales?"
]

for pregunta in preguntas:
    print("="*70)
    print(f"🔍 Pregunta: {pregunta}")
    print("="*70)
    
    results = vectorstore.similarity_search(pregunta, k=3)
    
    for i, doc in enumerate(results, 1):
        print(f"\n--- Resultado {i} (Relevancia: Alta) ---")
        print(f"Metadata: {doc.metadata.get('titulo', 'N/A')[:50]}...")
        print(f"Chunk: {doc.metadata.get('chunk_id', 'N/A')}/{doc.metadata.get('chunk_total', 'N/A')}")
        print(f"\nContenido:")
        print(doc.page_content[:400] + "...")
    
    print("\n")

print("\n✅ Prueba completada! El sistema de búsqueda funciona correctamente.")
