# ADR 0002: Motor Vectorial RAG

**Fecha:** 16 Marzo 2026
**Estatus:** Aceptado

## 1. Contexto y Problema
En **trIAje**, la precisión jurídica es innegociable. Los grandes modelos de lenguaje (LLMs) como GPT-4o son propensos a la alucinación (inventar artículos o plazos) si se les confía el conocimiento jurídico de forma nativa. 

El modelo de recuperación aumentada por generación (Retrieval-Augmented Generation o RAG) es nuestra técnica para solventar este problema: el sistema debe inyectar párrafos específicos y correctos del Código Civil o los Reglamentos de ONGs antes de solicitar al LLM que responda.

Necesitamos una Base de Datos Vectorial para almacenar textos embebidos semánticamente, que ofrezca:
1. Gratuidad extrema o Self-Hosting para MVP.
2. Latencia bajísima de búsqueda por similitud de coseno o L2.
3. Alta interoperabilidad con Python y SentenceTransformers (HuggingFace).

## 2. Opciones Consideradas

### A. Pinecone (BaaS - Backend as a Service)
*   Positivo: Integración instantánea, escalabilidad masiva y sinOps.
*   Negativo: Nivel gratuito muy restrictivo (1 solo índice). La facturación por pods escalaría rápidamente si indexamos la biblioteca legal completa peruana (Tributario, Laboral, Civil).

### B. PostgreSQL + pgvector
*   Positivo: Ya tendríamos la base de datos relacional (PosgreSQL) sirviendo también para vectores. ACID compliance total. Es el estándar de oro (Datakeeper's choice).
*   Negativo: Requiere un despliegue de PostgreSQL ajustado para RAM y compresión (IVFFlat o HNSW) desde el inicio, exigiendo un SysAdmin para configurar índices correctamente y perdiendo agilidad hiper-veloz para el prototipo.

### C. ChromaDB
*   Positivo: Funciona 100% en local y en memoria RAM con respaldo de SQLite (Persistencia en disco). Open source, gratuito. El API de Python es excelente. No exige instalar ningún runtime o daemon separado durante el desarrollo del MVP; se integra directo al ambiente de FastAPI.
*   Negativo: La concurrencia extrema (miles de QPS) no es su fuerte en modo local/memoria. Tendrá que mutar a *Chroma Server Dockerizado* o `pgvector` en el futuro.

## 3. Decisión Tomada

Nos decantamos por **ChromaDB** persistente en disco (carpeta `./chroma_data`) combinada con embeddings multilingües gratuitos de HuggingFace (`sentence-transformers/paraphrase-multilingual-mpnet-base-v2`).

Para la extracción del texto riguroso de normativas (PDFs a Markdown estructurado), se determinó el uso principal de **LlamaParse** para PDFs complejos con tablas (ej. Tarifarios registrales) y **PyMuPDF** para textos planos por ser local y sin costo por API.

## 4. Consecuencias (Trade-offs)

### Positivas
- **Cero Costo de Infraestructura:** La indexación de miles de chunks de normativas legales se realiza localmente utilizando la CPU del servidor (sin pagar APIs externas de embeddings como `text-embedding-3-small` de OpenAI). Solo pagamos los tokens generativos del chat de la inferencia.
- **Portabilidad Absoluta:** Basta con mover la carpeta `chroma_data` a otro servidor para tener la inteligencia legal migrada. No requiere Dumps sofisticados.

### Negativas / Riesgos
- **Escala Vertical:** Al ser el almacenamiento en memoria (Mapeado a disco), si la base legal peruana crece a gigabytes, la RAM del contenedor Docker (BackEnd) tendrá que escalar directamente o causar *OOM Kills* (Out Of Memory).
- **Cuellos de Botella (I/O Disk):** Usar SQLite como motor bajo *Chroma local* bloquea la escritura. No es recomendable para sistemas donde los datos legales cambian asíncronamente mientras 1000 usuarios consultan simultáneamente. *Plan de mitigación:* Cambiar modo `CHROMA_MODE=server` corriendo su propio contenedor aislado (Docker-Compose) antes del paso a producción (Visto en el archivo de despliegue).
