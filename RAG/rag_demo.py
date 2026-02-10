"""
Sistema RAG Completo - Demo
Combina ChromaDB (PDFs) + Respuestas Modelo (.md) + GPT
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai import OpenAI

# Configuración de rutas absolutas
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base"
CHROMA_DB_PATH = BASE_DIR / "chroma_db"
ENV_PATH = BASE_DIR / ".env"

# Cargar variables de entorno desde la ruta específica
load_dotenv(dotenv_path=ENV_PATH)

# Configuración
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

class LegalRAG:
    """Sistema RAG para asistencia legal a ONGs"""
    
    def __init__(self):
        """Inicializar componentes del RAG"""
        print("🚀 Inicializando sistema RAG...")
        
        # Inicializar embeddings
        print("   Cargando modelo de embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        )
        
        # Conectar a ChromaDB
        print("   Conectando a ChromaDB...")
        self.vectorstore = Chroma(
            persist_directory=str(CHROMA_DB_PATH),
            embedding_function=self.embeddings,
            collection_name="leyes_peru"
        )
        
        # Inicializar cliente OpenAI
        print("   Configurando OpenAI...")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        print(f"✅ Sistema RAG listo ({self.vectorstore._collection.count()} documentos)\n")
    
    def buscar_en_pdfs(self, query: str, k: int = 5):
        """Buscar artículos relevantes en PDFs (ChromaDB)"""
        print(f"🔍 Buscando en PDFs: '{query}'")
        results = self.vectorstore.similarity_search(query, k=k)
        print(f"   Encontrados {len(results)} artículos relevantes")
        return results
    
    def buscar_respuesta_modelo(self, intencion: str = "formalizacion"):
        """Buscar respuestas modelo en archivos .md"""
        print(f"📚 Buscando respuestas modelo en intención '{intencion}'...")
        
        respuestas_path = KNOWLEDGE_BASE_PATH / "intenciones" / f"01_{intencion}" / "construir_asociacion_civil_ong"
        
        if not respuestas_path.exists():
            print(f"   ⚠️  No se encontraron respuestas modelo")
            return []
        
        respuestas = []
        for md_file in respuestas_path.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                respuestas.append({
                    "archivo": md_file.name,
                    "contenido": content[:2000]  # Primeros 2000 caracteres
                })
        
        print(f"   Encontradas {len(respuestas)} respuestas modelo")
        return respuestas
    
    def generar_respuesta(self, query: str, articulos, respuestas_modelo):
        """Usar GPT para generar respuesta combinando artículos y respuestas modelo"""
        print(f"🤖 Generando respuesta con {OPENAI_MODEL}...")
        
        # Construir contexto de artículos
        contexto_articulos = "\n\n".join([
            f"[Artículo {i+1}]\n{doc.page_content[:500]}..."
            for i, doc in enumerate(articulos[:3])
        ])
        
        # Construir contexto de respuestas modelo
        contexto_respuestas = "\n\n".join([
            f"[Respuesta Modelo: {r['archivo']}]\n{r['contenido'][:800]}..."
            for r in respuestas_modelo[:2]
        ])
        
        # Prompt para GPT
        prompt = f"""Eres un asistente legal especializado en ONGs en Perú. Responde la pregunta del usuario de forma estructurada y didáctica.

CONTEXTO DE ARTÍCULOS LEGALES:
{contexto_articulos}

RESPUESTAS MODELO (usa estas como guía de estructura):
{contexto_respuestas}

PREGUNTA DEL USUARIO:
{query}

INSTRUCCIONES:
1. Responde de forma clara y estructurada (usa markdown)
2. Si hay respuestas modelo, úsalas como guía de estructura
3. Cita los artículos legales relevantes específicamente
4. Si la pregunta es sobre un proceso, explica paso a paso
5. Sé conciso pero completo

RESPUESTA:"""

        # Llamar a GPT
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Eres un asistente legal especializado en ONGs en Perú. Respondes con claridad, estructura y citando fuentes legales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Respuestas más consistentes
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def responder(self, query: str, intencion: str = "formalizacion"):
        """Responder pregunta del usuario usando RAG completo"""
        print("="*70)
        print(f"📝 PREGUNTA: {query}")
        print("="*70)
        print()
        
        # 1. Buscar en PDFs
        articulos = self.buscar_en_pdfs(query)
        print()
        
        # 2. Buscar respuestas modelo
        respuestas_modelo = self.buscar_respuesta_modelo(intencion)
        print()
        
        # 3. Generar respuesta con GPT
        respuesta = self.generar_respuesta(query, articulos, respuestas_modelo)
        print()
        
        # Mostrar resultado
        print("="*70)
        print("✨ RESPUESTA GENERADA")
        print("="*70)
        print()
        print(respuesta)
        print()
        print("="*70)
        print("📚 FUENTES CONSULTADAS")
        print("="*70)
        print(f"- {len(articulos)} artículos de PDFs legales")
        print(f"- {len(respuestas_modelo)} respuestas modelo")
        print(f"- Modelo: {OPENAI_MODEL}")
        print("="*70)
        print()
        
        return respuesta


def main():
    """Función principal - Demo del sistema RAG"""
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY no está configurada en .env")
        print("\nAgrega tu API key en el archivo .env:")
        print("OPENAI_API_KEY=tu-api-key-aqui")
        return
    
    # Inicializar RAG
    rag = LegalRAG()
    
    # Preguntas de prueba
    preguntas = [
        "¿Cuáles son los elementos obligatorios del estatuto de una asociación?",
        "¿En qué consiste la escritura pública para constituir una ONG?",
        "¿Qué documentos necesito para inscribir una asociación en SUNARP?",
    ]
    
    print("🎯 PROBANDO SISTEMA RAG CON 3 PREGUNTAS\n")
    
    for i, pregunta in enumerate(preguntas, 1):
        print(f"\n{'='*70}")
        print(f"PREGUNTA {i}/{len(preguntas)}")
        print(f"{'='*70}\n")
        
        rag.responder(pregunta)
        
        if i < len(preguntas):
            input("\n⏸️  Presiona Enter para continuar a la siguiente pregunta...\n")
    
    print("\n✅ Demo completada!")
    print("\nPara usar el sistema:")
    print("  from rag_demo import LegalRAG")
    print("  rag = LegalRAG()")
    print("  rag.responder('tu pregunta aquí')")


if __name__ == "__main__":
    main()
