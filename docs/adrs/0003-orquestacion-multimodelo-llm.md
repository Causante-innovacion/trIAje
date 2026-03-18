# ADR 0003: Orquestación Multi-Modelo (Routing LLM)

**Fecha:** 16 Marzo 2026
**Estatus:** Aceptado

## 1. Contexto y Problema
En el flujo de **trIAje**, no todas las tareas de IA requieren el mismo nivel de procesamiento cognitivo ni tienen el mismo costo computacional.
Tenemos tres grandes tipos de tareas:
1.  **Intake (Clasificación e Ingesta):** Leer el formulario del usuario, normalizar datos y extraer intenciones legales. Es una tarea de extracción rápida.
2.  **Reasoning (Razonamiento Legal):** Cruzar la intención del usuario con los documentos legales (RAG) y emitir un juicio de viabilidad o responder dudas complejas. Requiere "Cadena de Pensamiento" (Chain of Thought).
3.  **Creativity (Redacción):** Generar resúmenes, actas o correos para el usuario final basados en el razonamiento previo.

Usar un modelo gigante (como GPT-4) para las tres tareas es prohibitivamente caro y lento. Usar un modelo pequeño para el razonamiento legal es peligroso jurídicamente.

## 2. Opciones Consideradas

### A. Proveedor Único (Ej: Todo con OpenAI)
*   **Gestión:** Muy simple (solo requiere `OPENAI_API_KEY`).
*   **Problema:** Dependencia absoluta del ecosistema de un solo proveedor (*Vendor Lock-in*), costos inflexibles y falta de acceso a modelos altamente especializados en razonamiento (como DeepSeek-R1) o modelos *open source* económicos.

### B. Enrutador LLM Agnostic (LangChain / Maple AI)
*   **Gestión:** Utilizar la abstracción `BaseChatModel` de LangChain combinada con un proxy/provider como **Maple AI** que permite consumir múltiples modelos (OpenSource y Privativos) bajo una misma interfaz compatible con OpenAI.
*   **Beneficio:** Permite asignar el modelo idóneo y más eficiente por cada tarea específica (Routing por módulo).

## 3. Decisión Tomada

Se implementó una arquitectura de **Routing por Módulo** (`app/ai/router.py`) apoyada nativamente en **Maple AI** como proveedor principal de modelos integrados.

La distribución actual de la carga de trabajo es la siguiente:

1.  **Módulo INTAKE (`MODEL_INTAKE`):**
    *   **Modelo:** **Llama** (o modelos rápidos/Open source vía Maple AI).
    *   **Propósito:** Procesamiento casi instantáneo para normalizar el JSON de entrada y decidir qué herramienta debe ejecutarse. Configurado con baja temperatura (`temperature=0.3`).
2.  **Módulo REASONING (`MODEL_REASONING`):**
    *   **Modelo:** **DeepSeek-R1** (consumido vía Maple AI).
    *   **Propósito:** Razonamiento complejo. Este modelo utiliza el bloque `<think>` (Cadena de Pensamiento). Se le inyecta un *prefill* por sistema para obligarlo a razonar y estructurar sus pensamientos **estrictamente en español** antes de emitir un veredicto legal basado en el RAG.
3.  **Módulo CREATIVITY (`MODEL_CREATIVITY`):**
    *   **Modelo:** Modelos base Open Source compatibles con OpenAI API (o *Claude-Sonnet* como alternativa).
    *   **Propósito:** Redacción fluida y generación de documentos finales.

## 4. Consecuencias (Trade-offs)

### Positivas (Qué ganamos)
- **Eficiencia de Costos y Precisión:** El razonamiento profundo se delega a DeepSeek (excelente en lógica), mientras que la extracción rutinaria se hace con Llama (rápido y barato).
- **Flexibilidad (Zero Lock-in):** Si sale un modelo mejor mañana, su integración solo requiere cambiar una variable de entorno en `.env` (ej. `MODEL_REASONING=nuevo-modelo`) sin modificar la lógica del código backend, ya que la clase `AIRouter` es agnóstica.
- **Privacidad y Seguridad:** Al utilizar Maple AI o modelos de código abierto, se reduce la exposición de los datos legales de las ONGs hacia infraestructuras de propósito general, permitiendo un nivel de anonimización mayor.

### Negativas / Riesgos (Deuda técnica asumida)
- **Bloques de Pensamiento Explicítos:** Modelos como DeepSeek-R1 devuelven sus razonamientos en bloques `<think>`. El Router (`router.py`) tiene que inyectar cabeceras especiales en español para que el modelo no razone en inglés y arruine el parseo del Frontend, requiriendo un manejo de *streaming* (texto iterativo) más delicado.
- **Latencia de Redirección:** Depender de un proxy multiplicador (como Maple AI) significa que, si ese servicio intermediario cae, todo el sistema de IA pierde la conexión a sus sub-modelos.
