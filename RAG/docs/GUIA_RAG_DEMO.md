# 🚀 Guía de Uso - Sistema RAG Completo

## ¿Qué Hace Este Sistema?

El `rag_demo.py` combina **3 fuentes de información**:

1. **ChromaDB** (PDFs procesados) → Artículos legales
2. **Respuestas Modelo** (.md files) → Guías estructuradas
3. **GPT** → Genera respuesta natural combinando 1 + 2

---

## 📋 Paso 1: Configurar API Key de OpenAI

Edita el archivo `.env` y agrega tu API key:

```bash
LLAMA_CLOUD_API_KEY=llx-tu-key-aqui
OPENAI_API_KEY=sk-tu-openai-key-aqui  # ← AGREGAR ESTA LÍNEA
```

**¿Dónde conseguir API key?**
1. Ve a: https://platform.openai.com/api-keys
2. Crea una nueva key
3. Copia y pega en `.env`

---

## 🚀 Paso 2: Ejecutar Demo

```powershell
.\venv\Scripts\python.exe rag_demo.py
```

El sistema probará 3 preguntas automáticamente:
- Elementos del estatuto
- Escritura pública
- Documentos para SUNARP

---

## 🎯 Cómo Funciona

### Flujo del Sistema

```
Usuario: "¿Cuáles son los elementos del estatuto?"
    ↓
1. BUSCAR EN CHROMADB
   → Encuentra 5 artículos relevantes de los PDFs
   → Ej: Art. 14 del Reglamento PJ
    ↓
2. BUSCAR RESPUESTAS MODELO
   → Lee archivos .md en intenciones/formalizacion/
   → Ej: 6_elementos_estatutos_asociacion.md
    ↓
3. ENVIAR A GPT
   Prompt: "Aquí están los artículos + las respuestas modelo.
           Genera una respuesta estructurada citando fuentes."
    ↓
4. GPT GENERA RESPUESTA
   → Usa estructura de respuestas modelo
   → Cita artículos específicos
   → Respuesta clara y paso a paso
    ↓
Usuario ← Respuesta Final
```

---

## 📊 Diferencias vs test_busqueda.py

| Aspecto | test_busqueda.py | rag_demo.py |
|---------|------------------|-------------|
| **Busca en PDFs** | ✅ Sí | ✅ Sí |
| **Busca respuestas modelo** | ❌ No | ✅ Sí |
| **Genera respuesta** | ❌ No, solo muestra artículos | ✅ Sí, con GPT |
| **Estructura paso a paso** | ❌ No | ✅ Sí |
| **Cita fuentes** | Básico | ✅ Específicas |
| **Requiere API key** | No | Sí (OpenAI) |

---

## 💡 Ejemplo de Salida

**Pregunta**: "¿Cuáles son los elementos del estatuto?"

**Respuesta del Sistema**:
```markdown
# Elementos Obligatorios del Estatuto

Según el Reglamento de Inscripciones (Art. 14), el estatuto debe contener:

## 1. Datos de Identificación
- Denominación completa y domicilio
- Objeto social y fines

## 2. Estructura Organizativa
- Órganos de gobierno (Asamblea, Directiva)
- Requisitos para ser asociado
- Derechos y obligaciones de asociados

## 3. Aspectos Económicos
- Patrimonio y recursos
- Régimen económico

## 4. Aspectos Operativos
- ...

**Fundamento legal**: Art. 14, Reglamento de Inscripciones PJ
```

---

## ⚙️ Configuración Avanzada

### Cambiar Modelo GPT

En `.env`:
```bash
# Más barato y rápido (recomendado para pruebas)
OPENAI_MODEL=gpt-3.5-turbo

# Más preciso pero más caro
OPENAI_MODEL=gpt-4

# Más nuevo (recomendado producción)
OPENAI_MODEL=gpt-4o-mini
```

### Costos Aproximados

| Modelo | Costo por pregunta | Calidad |
|--------|-------------------|---------|
| gpt-3.5-turbo | ~$0.01 | Buena ✅ |
| gpt-4o-mini | ~$0.02 | Muy buena ✅✅ |
| gpt-4 | ~$0.10 | Excelente ✅✅✅ |

---

## 🔧 Uso Programático

```python
from rag_demo import LegalRAG

# Inicializar sistema
rag = LegalRAG()

# Hacer pregunta
respuesta = rag.responder(
    "¿Qué es el parte notarial?",
    intencion="formalizacion"
)

print(respuesta)
```

---

## 🎯 Próximos Pasos

Después de probar este demo:

1. **Agregar clasificadores** automáticos de intención y riesgo
2. **Crear más respuestas modelo** para otras intenciones
3. **Integrar en API Flask/FastAPI** para uso web
4. **Agregar memoria conversacional** para seguimiento de contexto

---

## ❓ Troubleshooting

### Error: "OPENAI_API_KEY no está configurada"
**Solución**: Agrega la key en el archivo `.env`

### Error: "No module named 'openai'"
**Solución**: `.\venv\Scripts\python.exe -m pip install openai`

### Respuestas genéricas o irrelevantes
**Causas**:
- Pocas respuestas modelo (crea más)
- PDFs no relevantes (agrega más)
- Temperatura alta (ajusta en código)

**Solución**: Crear más respuestas modelo en `knowledge_base/intenciones/`

---

## ✅ Checklist

Antes de ejecutar:
- [ ] API key de OpenAI en `.env`
- [ ] ChromaDB con chunks (verificar con `test_busqueda.py`)
- [ ] Al menos 1-2 respuestas modelo en `intenciones/formalizacion/`
- [ ] Entorno virtual activado

---

## 🚀 Comando Rápido

```powershell
# Ejecutar demo
.\venv\Scripts\python.exe rag_demo.py
```

¡Listo! Ahora tienes un RAG que genera respuestas como tus respuestas modelo 🎉
