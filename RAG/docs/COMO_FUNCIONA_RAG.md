# 🧠 Cómo Funcionará GPT Legal - Arquitectura RAG Explicada

## Tu Pregunta Clave

> "Si respondemos todas las preguntas, ¿no es solo una base de datos?  
> ¿Qué pasa si el usuario pregunta de forma diferente?"

**Respuesta corta**: NO es una BD simple. El RAG usa **búsqueda semántica** + **LLM** para entender preguntas formuladas de cualquier manera y generar respuestas contextuales.

---

## ❌ Lo que NO es RAG (Base de Datos Tradicional)

### Sistema de BD Simple (IF-THEN)

```python
# ❌ Esto NO es lo que haremos
preguntas_bd = {
    "¿Cómo constituir una asociación?": "Respuesta A",
    "¿Qué pasos seguir para formalizar?": "Respuesta B"
}

# Problema: Solo funciona con texto EXACTO
usuario_pregunta = "¿Cómo hago para crear una ONG?"
respuesta = preguntas_bd.get(usuario_pregunta)  # ❌ None - no encuentra match
```

**Problemas**:
- Solo coincide texto exacto
- No entiende sinónimos
- No combina información
- No responde variaciones

---

## ✅ Lo que SÍ es RAG (Retrieval Augmented Generation)

### 1. Búsqueda Semántica (Entender el Significado)

RAG convierte texto a **vectores numéricos** (embeddings) que capturan el **significado**:

```python
# ✅ Así funciona RAG con embeddings

# Todas estas preguntas tienen embeddings SIMILARES:
pregunta_1 = "¿Cómo constituir una asociación?"          → [0.8, 0.2, 0.5, ...]
pregunta_2 = "¿Qué pasos para formalizar mi ONG?"        → [0.79, 0.21, 0.52, ...]
pregunta_3 = "Quiero crear una organización sin lucro"  → [0.78, 0.19, 0.51, ...]
pregunta_4 = "Help me start a nonprofit in Peru"        → [0.77, 0.22, 0.49, ...]

# El sistema calcula SIMILITUD entre vectores
# Aunque las palabras sean diferentes, el SIGNIFICADO es similar
```

**Resultado**: El RAG encuentra las respuestas relevantes **sin importar cómo pregunte el usuario**.

---

### 2. Generación con Contexto (LLM)

El LLM (GPT, Claude, etc.) **genera** la respuesta usando:
- Los documentos recuperados (respuestas modelo + leyes)
- El contexto del usuario (Ficha Legal Mínima)
- Prompt específico por color (verde/amarillo/rojo)

```python
# Flujo simplificado
def responder_pregunta(pregunta_usuario):
    # 1. Convertir pregunta a vector
    embedding_pregunta = generar_embedding(pregunta_usuario)
    
    # 2. Buscar documentos similares en ChromaDB
    documentos_relevantes = chromadb.buscar_similares(
        embedding_pregunta, 
        coleccion="formalizacion",  # Según intención detectada
        top_k=5  # Top 5 más relevantes
    )
    
    # 3. Construir prompt para LLM
    prompt = f"""
    Contexto relevante:
    {documentos_relevantes}
    
    Usuario pregunta: {pregunta_usuario}
    
    Responde de forma clara, paso a paso, citando fuentes.
    """
    
    # 4. LLM genera respuesta
    respuesta = llm.generar(prompt)
    
    return respuesta
```

---

## 🎯 Arquitectura Completa de GPT Legal

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO PREGUNTA                          │
│  "Quiero crear una ONG educativa, ¿qué necesito?"           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│        PASO 1: CLASIFICACIÓN DE INTENCIÓN                   │
│  - Analiza keywords y contexto                              │
│  - Detecta: "crear ONG" → Intención: FORMALIZACION         │
│  - Salida: intention="formalizacion"                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│        PASO 2: CLASIFICACIÓN DE RIESGO                      │
│  - Analiza complejidad de la pregunta                       │
│  - No menciona conflictos/multas → VERDE                    │
│  - Salida: color="verde"                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│        PASO 3: BÚSQUEDA SEMÁNTICA (RAG)                     │
│                                                              │
│  A) Convertir pregunta a embedding                          │
│     "crear ONG educativa" → [0.82, 0.15, 0.67, ...]        │
│                                                              │
│  B) Buscar en ChromaDB colección "formalizacion"           │
│     Top 5 documentos más similares:                         │
│     1. constitucion_asociacion.md (score: 0.95)            │
│     2. requisitos_legales.md (score: 0.89)                 │
│     3. Código Civil Art. 80-82 (score: 0.85)               │
│     4. pasos_formalizacion.md (score: 0.82)                │
│     5. SUNARP_procedimiento.pdf chunk (score: 0.78)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│        PASO 4: RECOPILACIÓN DE CONTEXTO                     │
│  - Ficha Legal Mínima: ¿Ya está formalizada? → No          │
│  - ¿Cuántos fundadores? → 3 personas                        │
│  - Domicilio: Lima                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│        PASO 5: GENERACIÓN DE RESPUESTA (LLM)                │
│                                                              │
│  Prompt construido:                                         │
│  ─────────────────────────────────────────────              │
│  Sistema: Eres asesor legal para ONGs en Perú              │
│                                                              │
│  Color: VERDE (respuesta paso a paso, autoservicio)         │
│                                                              │
│  Contexto del usuario:                                      │
│  - 3 fundadores                                             │
│  - No formalizada aún                                       │
│  - En Lima                                                  │
│                                                              │
│  Documentos relevantes:                                     │
│  [Contenido de los 5 documentos recuperados]                │
│                                                              │
│  Pregunta: "Quiero crear una ONG educativa, ¿qué necesito?"│
│                                                              │
│  Instrucciones:                                             │
│  - Responde paso a paso                                     │
│  - Incluye costos y tiempos                                 │
│  - Cita artículos relevantes                                │
│  - Adapta a su contexto (3 fundadores, Lima)                │
│  ─────────────────────────────────────────────              │
│                                                              │
│  LLM genera respuesta personalizada ↓                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 RESPUESTA AL USUARIO                         │
│                                                              │
│  "Para crear una ONG educativa con 3 fundadores en Lima:   │
│                                                              │
│  1. Reservar nombre en SUNARP (S/. 20, 1-2 días)           │
│  2. Elaborar minuta con los 3 fundadores...                 │
│  3. Escritura pública (S/. 300-500, 5-7 días)               │
│  [...]                                                       │
│                                                              │
│  Fuentes:                                                    │
│  - Código Civil Arts. 80, 82                                │
│  - constitucion_asociacion.md                                │
│  - SUNARP procedimiento                                     │
│                                                              │
│  Próximo paso: ¿Ya tienen el nombre de la ONG?             │
│  [Pregunta de Ficha Legal para recopilar más contexto]     │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Por Qué Necesitamos AMBOS: Respuestas Modelo + Documentos Legales

### 1. Respuestas Modelo (Lo que estás creando ahora)

**Propósito**:
- Explicaciones **didácticas** paso a paso
- Lenguaje **simple y accesible**
- Ejemplos prácticos
- Costos, tiempos estimados

**Ejemplo**: `constitucion_asociacion.md`
- Escrito pensando en ONGs sin experiencia legal
- Explica el "por qué" de cada paso

### 2. Documentos Legales (PDFs de leyes)

**Propósito**:
- Texto **legal oficial**
- Artículos específicos
- Normativa exacta
- Fuente de verdad legal

**Ejemplo**: `Código Civil Art. 82`
- Texto de ley literal
- Para citas precisas

### 3. Cómo se Combinan

El LLM usa **AMBOS** para generar respuestas:

```
Usuario: "¿Cuántos fundadores mínimo necesito?"

ChromaDB recupera:
1. constitucion_asociacion.md → "Mínimo 2 personas (según Art. 82)"
2. Código Civil chunk → "Art. 82: La asociación debe estar constituida 
   por dos o más personas"
3. requisitos_legales.md → "2 fundadores mínimo, pueden ser naturales 
   o jurídicas"

LLM combina y genera:
"Necesitas mínimo 2 fundadores según el Artículo 82 del Código Civil.
Pueden ser personas naturales (con DNI) o jurídicas (otras organizaciones).

Fuentes:
- Código Civil Art. 82
- Guía de Constitución de Asociaciones"
```

---

## 🔄 Ejemplo Real: Misma Pregunta, 3 Formas Diferentes

### Usuario 1:
> "¿Cómo constituir una asociación civil?"

### Usuario 2:
> "Quiero formalizar mi ONG, ¿qué hago?"

### Usuario 3:
> "Pasos para crear organización sin fines de lucro"

### ¿Qué Pasa en el RAG?

```python
# Los 3 generan embeddings SIMILARES

embedding_1 = [0.82, 0.15, 0.67, 0.23, ...]  # "constituir asociación"
embedding_2 = [0.81, 0.16, 0.66, 0.24, ...]  # "formalizar ONG"
embedding_3 = [0.80, 0.14, 0.68, 0.22, ...]  # "crear sin fines lucro"

# ChromaDB calcula similitud coseno
similitud(embedding_1, embedding_2) = 0.98  # Muy similar
similitud(embedding_1, embedding_3) = 0.96  # Muy similar

# Resultado: Los 3 recuperan los MISMOS documentos relevantes
```

**Todos obtienen la misma información base**, pero el LLM adapta la respuesta al estilo de cada pregunta.

---

## 📚 Los 3 Componentes del Knowledge Base

### 1. Respuestas Modelo (Intenciones)
```
knowledge_base/intenciones/01_formalizacion/
├── constitucion_asociacion.md
├── requisitos_legales.md
└── ...
```
**Función**: Explicaciones didácticas

### 2. Documentos Legales (Normas)
```
knowledge_base/normas/tributario/
├── ley_impuesto_renta.pdf
└── codigo_tributario.pdf
```
**Función**: Texto legal oficial

### 3. Catálogo de Preguntas
```
knowledge_base/preguntas/
├── preguntas_estandar.json
└── preguntas_complejas.json
```
**Función**: Entrenamiento del clasificador de intenciones

---

## 🎯 Próximos Pasos Correctos para Armar GPT Legal

### FASE 1: Knowledge Base (EN CURSO ✅)
- [x] Crear respuestas modelo (✅ Ya tienes 7 en formalización)
- [ ] Descargar 3-5 PDFs de leyes principales
- [ ] Crear metadata para cada PDF
- [ ] Procesar con ETL → ChromaDB

**Meta**: Tener colecciones con contenido vectorizado

---

### FASE 2: Clasificadores (PRÓXIMO PASO)

#### A. Clasificador de Intenciones

```python
# rag_system/classification/intention_classifier.py

class IntentionClassifier:
    def classify(self, pregunta: str) -> str:
        """
        Detecta la intención de la pregunta
        
        Entrada: "Quiero crear una ONG"
        Salida: "formalizacion"
        """
        # Implementación simple: keywords
        # Implementación avanzada: modelo ML
```

#### B. Clasificador de Riesgo

```python
# rag_system/classification/risk_classifier.py

class RiskClassifier:
    def classify(self, pregunta: str, intencion: str) -> str:
        """
        Determina el color (verde/amarillo/rojo)
        
        Entrada: "Tengo multa de SUNAT"
        Salida: "rojo" → Derivar a abogado
        """
```

---

### FASE 3: RAG Pipeline (DESPUÉS)

```python
# rag_system/rag/intention_rag.py

class IntentionBasedRAG:
    def query(self, pregunta: str) -> dict:
        # 1. Clasificar intención
        intencion = self.intention_classifier.classify(pregunta)
        
        # 2. Clasificar riesgo
        color = self.risk_classifier.classify(pregunta, intencion)
        
        # 3. Buscar en colección específica
        docs = self.chromadb.query(
            collection=f"col_{intencion}",
            query=pregunta,
            n_results=5
        )
        
        # 4. Recopilar contexto (Ficha Legal)
        contexto = self.ficha_legal.get_context()
        
        # 5. Generar respuesta con LLM
        respuesta = self.llm.generate(
            prompt=self.build_prompt(color, docs, contexto, pregunta)
        )
        
        return {
            "respuesta": respuesta,
            "color": color,
            "fuentes": docs,
            "siguiente_pregunta_ficha": self.ficha_legal.next_question(intencion)
        }
```

---

### FASE 4: Ficha Legal Mínima (OPCIONAL FASE 1)

Sistema para recopilar contexto del usuario progresivamente:

```python
# Si detecta intención "tributacion"
ficha_legal.ask("fuentes_ingreso")  
# → "¿Tu ONG genera ingresos por servicios?"

# Si detecta "cooperacion"
ficha_legal.ask("registro_apci")
# → "¿Ya estás inscrito en APCI?"
```

---

### FASE 5: Testing y Ajustes

- Probar con preguntas reales
- Ajustar prompts por color
- Mejorar clasificadores
- Agregar más documentos

---

## 🚀 Roadmap Resumido

| Semana | Actividad | Estado |
|--------|-----------|--------|
| **1-2** | Crear 20-30 respuestas modelo | 🔄 En progreso |
| **2-3** | Descargar y procesar 5 PDFs de leyes | ⏳ Pendiente |
| **3-4** | Implementar clasificadores (intención + riesgo) | ⏳ Pendiente |
| **4-5** | Implementar RAG pipeline básico | ⏳ Pendiente |
| **5-6** | Testing con preguntas reales | ⏳ Pendiente |
| **6+** | Ficha Legal Mínima (opcional) | ⏳ Pendiente |

---

## 💬 Respondiendo Tu Pregunta Original

### "¿No es solo una BD?"

**No**, porque:
1. ✅ Usa **búsqueda semántica** (entiende sinónimos, variaciones)
2. ✅ **Combina** múltiples fuentes de información
3. ✅ **Genera** respuestas adaptadas al contexto del usuario
4. ✅ **Cita** fuentes legales precisas
5. ✅ **Aprende** de documentos que agregas sin reprogramar

### "¿Qué si preguntan diferente?"

**Funciona igual**, porque:
- Los embeddings capturan **significado**, no palabras exactas
- El LLM **reformula** la respuesta según cómo preguntó el usuario
- ChromaDB encuentra documentos **semánticamente similares**

---

## 🎯 Próximo Paso Inmediato

**AHORA** (esta semana):
1. Continuar creando 10-15 respuestas modelo más en otras intenciones
2. Descargar 2-3 PDFs de leyes (Código Civil, Ley IR)
3. Crear metadata JSON para cada PDF

**PRÓXIMA SEMANA**:
1. Procesar PDFs con ETL → ChromaDB
2. Implementar clasificador simple de intenciones
3. Primer test del RAG con búsqueda semántica

---

**¿Te quedó claro cómo funciona? ¿Alguna parte quieres que profundice más?**
