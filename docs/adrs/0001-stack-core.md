# ADR 0001: Arquitectura Core de Software

**Fecha:** 16 Marzo 2026
**Estatus:** Aceptado

## 1. Contexto y Problema
El objetivo principal de **trIAje** es actuar como asistente jurídico especializado para el Tercer Sector. Se requiere procesar consultas de usuarios (NLP), cruzar esa intención con una base documental de alta densidad semántica (Leyes peruanas y Modelos de asesoría), y retornar una respuesta rápida con muy baja tolerancia al error u alucinación.

Necesitamos una base de arquitectura que cumpla con:
- Desarrollo rápido (MVP).
- Alta concurrencia para procesamiento de IA asíncrono.
- Separación estricta entre presentación (Frontend) y lógica (Backend) para no acoplar la web a los flujos del agente.

## 2. Opciones Consideradas

### A. Para el Backend (Lógica de Negocio e IA)
*   **Express/Node.js:** Excelente ecosistema, pero débil para manejo intensivo de estructuras de datos (Machine Learning) y carece de tipado estricto por defecto (sin TS).
*   **Django:** Muy robusto, pero el ORM y la estructura monolítica es "demasiado grande" para un MVP muy apoyado en servicios externos (OpenAI) y una base de datos más orientada a vectores que a diagramas relacionales completos.
*   **FastAPI (Python):** Ligero, validación de datos garantizada de fábrica con Pydantic, soporte asíncrono puro (`async/await`) ideal para APIs lentas de IA, y vive en el mismo ecosistema (Python) donde ocurre el 95% del desarrollo en IA / Data Science.

### B. Para el Frontend (UI/UX)
*   **Vanilla JS / HTML:** Rápido de arrancar pero insostenible para estados complejos.
*   **Next.js (App Router):** Excelente para SEO, pero introduce complejidad de Server Side Rendering (SSR) que no requerimos para una plataforma (dashboard) cerrada por autenticación o uso directo interno.
*   **React (Single Page Application) + Vite:** Genera un empaquetado estático independiente (Desacoplado del backend), con recarga instantánea en desarrollo. Combinado con TypeScript previene errores de consumo de la API.

## 3. Decisión Tomada

Hemos adoptado el siguiente stack tecnológico principal:

**Backend:**
- **FastAPI (Python 3.11+)** como framework web asíncrono.
- **Pydantic v2** para la sanitización, validación y serialización de Contratos de Datos (Schemas).

**Frontend:**
- **React (v18)** inicializado mediante **Vite**.
- **TypeScript** riguroso para la definición de componentes y respuestas de API.
- **Tailwind CSS** para estilo sin acoplamiento de librerías de componentes pesadas.

## 4. Consecuencias (Trade-offs)

### Positivas (Qué ganamos)
- **Ecosistema AI Directo:** FastAPI permite integrar bibliotecas como LangChain, ChromaDB y HuggingFace nativamente en Python sin puentes RPC ni microservicios separados.
- **Velocidad de Interfaz:** Al ser un SPA en Vite con Tailwind CSS, el frontend carece de cargas completas de página; la comunicación por fetch a FastAPI de forma asíncrona es excepcionalmente fluida.
- **Validación Bidireccional:** Podemos copiar casi directamente el contrato Pydantic del servidor hacia una interfaz (Type) en TS, reduciendo drásticamente las discrepancias cliente-servidor.

### Negativas / Riesgos (Deuda técnica asumida)
- **Bloqueos del Event Loop (Python):** Python tiene el GIL. Si hacemos análisis intensivo de CPU (como embeddings de vectores locales con `SentenceTransformers`) de forma paralela a una request de red, podríamos estrangular el servidor. Requiere monitoreo y eventual envío de tareas a *workers* separados (ej. Celery/Redis).
- **SEO Pobre:** Al ser un SPA (React/Vite) clásico, los motores de búsqueda sufrirán parseando la web. Dado que es una herramienta cerrada, este coste es aceptable.
