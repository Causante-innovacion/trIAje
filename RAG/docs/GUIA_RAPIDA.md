# 🚀 Guía Rápida: Implementar RAG en 1 Hora

## ⏱️ PASO A PASO INMEDIATO

### PASO 1: Crear Estructura de Carpetas (5 min)

```bash
cd c:\Users\usuario\Documents\GitHub\gpt-legal

# Crear carpetas
mkdir knowledge_base
mkdir knowledge_base\normas
mkdir knowledge_base\normas\sunat
mkdir knowledge_base\normas\apci
mkdir knowledge_base\normas\civil
mkdir knowledge_base\normas\laboral
mkdir knowledge_base\procedimientos
mkdir knowledge_base\metadata
mkdir rag_system
mkdir rag_system\etl
mkdir chroma_db
```

### PASO 2: Descargar Documentos Críticos (10 min)

**Opción A: Descarga Manual**

1. **Ley del Impuesto a la Renta**
   - URL: https://www.sunat.gob.pe/legislacion/renta/ley/fdetalle.htm
   - Guardar como: `knowledge_base\normas\sunat\ley_renta.pdf`

2. **Ley de Asociaciones**
   - URL: Buscar en Google "Ley 26370 Asociaciones sin fines de lucro PDF"
   - Guardar como: `knowledge_base\normas\civil\ley_asociaciones.pdf`

3. **Código Tributario**
   - URL: https://www.sunat.gob.pe/legislacion/codigo/
   - Guardar como: `knowledge_base\normas\sunat\codigo_tributario.pdf`

**Opción B: Script Automático**

```python
# TODO: Crear script download_docs.py
# Por ahora, descarga manual es más seguro
```

### PASO 3: Crear Metadatos (15 min)

Para CADA PDF descargado, crear un JSON en `knowledge_base\metadata\`:

**Ejemplo**: `knowledge_base\metadata\SUNAT_LIR_2023.json`

```json
{
  "doc_id": "SUNAT_LIR_2023",
  "titulo": "Ley del Impuesto a la Renta",
  "tipo": "norma",
  "categoria": "tributario",
  "entidad": "SUNAT",
  "url_oficial": "https://www.sunat.gob.pe/legislacion/renta/ley/fdetalle.htm",
  "archivo_local": "knowledge_base/normas/sunat/ley_renta.pdf",
  "keywords": ["impuesto", "renta", "ingresos", "ong"]
}
```

**⚠️ IMPORTANTE**: El nombre del archivo JSON debe coincidir con el nombre del PDF (sin extensión).

### PASO 4: Instalar Dependencias (5 min)

```bash
cd c:\Users\usuario\Documents\GitHub\gpt-legal

# Activar entorno virtual (si usas uno)
# .venv\Scripts\activate

# Instalar paquetes
pip install llama-parse
pip install langchain
pip install chromadb
pip install sentence-transformers
pip install langchain-community
```

### PASO 5: Obtener API Key de Llama Parse (5 min)

1. Ir a: https://cloud.llamaindex.ai/
2. Crear cuenta (gratis)
3. Obtener API Key
4. Crear archivo `.env`:

```bash
# .env
LLAMA_CLOUD_API_KEY=tu_api_key_aqui
```

### PASO 6: Procesar Primer Documento (10 min)

```bash
cd rag_system\etl

# Procesar un documento específico
python process_documents.py --doc ley_renta --api-key tu_api_key
```

**Output esperado**:
```
📄 Procesando: ley_renta.pdf
   ✂️  Creados 142 chunks
🧠 Cargando 142 chunks a ChromaDB...
✅ Carga completada a colección 'leyes_peru'
```

### PASO 7: Test de Búsqueda (5 min)

```python
# test_retrieval.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Cargar base vectorial
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

vectorstore = Chroma(
    persist_directory="../../chroma_db",
    embedding_function=embeddings,
    collection_name="leyes_peru"
)

# Hacer una pregunta de prueba
pregunta = "¿Pueden las ONGs generar ingresos por servicios?"
docs = vectorstore.similarity_search(pregunta, k=3)

# Ver resultados
for i, doc in enumerate(docs, 1):
    print(f"\n--- Resultado {i} ---")
    print(f"Documento: {doc.metadata.get('doc_id')}")
    print(f"Texto: {doc.page_content[:200]}...")
```

### PASO 8: Procesar Resto de Documentos (5 min)

```bash
# Procesar todos los documentos de SUNAT
python process_documents.py --category sunat --api-key tu_api_key

# Procesar TODAS las categorías
python process_documents.py --all --api-key tu_api_key
```

---

## 📋 CHECKLIST DE VALIDACIÓN

Después de completar los pasos, verificar:

- [ ] Carpeta `knowledge_base/` creada con subcarpetas
- [ ] Mínimo 3 PDFs descargados
- [ ] 3 archivos JSON de metadata creados
- [ ] Dependencias instaladas sin errores
- [ ] API key de llama-parse configurada
- [ ] ChromaDB creada en `chroma_db/`
- [ ] Test de búsqueda funciona y devuelve resultados

---

## 🆘 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'llama_parse'"
**Solución**: 
```bash
pip install llama-parse --upgrade
```

### Error: "API key not found"
**Solución**: 
- Verificar que el archivo `.env` existe
- O pasar API key directamente: `--api-key TU_KEY`

### Error: "PDF parsing failed"
**Solución**:
- Verificar que el PDF no esté corrupto
- Intentar con otro PDF más simple primero
- Revisar que llama-parse tenga créditos disponibles

### ChromaDB muy lento
**Solución**:
- Usar SSD en lugar de HDD
- Limitar cantidad de documentos en MVP
- Considerar usar embeddings de OpenAI (más rápido pero pago)

---

## 📊 MÉTRICAS ESPERADAS (MVP)

| Métrica | Valor Esperado |
|---------|----------------|
| Documentos procesados | 3-5 |
| Chunks totales | 300-500 |
| Tiempo de procesamiento | ~10 min |
| Tamaño ChromaDB | ~50-100 MB |
| Tiempo de búsqueda | <2 segundos |

---

## 🎯 PRÓXIMOS PASOS

Una vez que tengas el RAG básico funcionando:

1. **Integrar con FastAPI** → Ver `implementation_plan.md` Paso 8
2. **Crear prompts por modo** → Ver carpeta `rag_system/prompts/`
3. **Agregar sistema de citación** → Formatear referencias clickeables
4. **Test de calidad** → Validar con preguntas reales

---

## 📞 AYUDA

Si te atascas en algún paso, revisa:
- `implementation_plan.md` → Plan completo detallado
- `process_documents.py` → Código del ETL
- `EJEMPLO_SUNAT_LIR_2023.json` → Template de metadata
