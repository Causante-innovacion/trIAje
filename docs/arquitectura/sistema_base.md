# Arquitectura del Proyecto trIAje

Este documento define la estructura y arquitectura técnica del proyecto **trIAje**, diseñada para ser escalable, modular y cumplir con los requisitos de negocio (Causante).

## Stack Tecnológico

### Frontend (SPA)
- **Framework**: React (Vite)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **Estado/API**: TanStack Query
- **Formularios**: React Hook Form + Zod
- **Routing**: React Router

### Backend (API)
- **Framework**: FastAPI (Python)
- **Lógica de Agente**: LangChain / LangGraph (Orquestación de IAs)
- **Base de Datos**: PostgreSQL + pgvector (Recomendado para RAG y persistencia)

---

## Estructura de Directorios Propuesta

```bash
triaje/
├── backend/                  # API, lógica de IA y base de datos (Python)
├── README.md               # Punto de entrada y documentación general
├── docs/                   # Documentación detallada (Arquitectura, Guías)
│   └── ARCHITECTURE.md
│
├── frontend/               # Aplicación React (Vite)
│   ├── src/
│   │   ├── api/            # Clientes para conectar con FastAPI
│   │   ├── components/     # UI Reutilizable
│   │   │   ├── ui/         # Componentes base (Botones, Inputs - Shadcn/Tailwind)
│   │   │   ├── layout/     # Estructuras de página
│   │   │   └── traffic/    # Componentes de Semáforo (Verde/Amarillo)
│   │   ├── hooks/          # Lógica de estado (useProjectEvaluation)
│   │   ├── pages/          # Vistas (Dashboard, Herramientas 1-4)
│   │   ├── schemas/        # Validaciones Zod (compartidas conceptualmente con backend)
│   │   └── types/          # Definiciones TypeScript
│   ├── public/
│   └── vite.config.ts
│
└── backend/                # API Python FastAPI
    ├── app/
    │   ├── main.py         # Punto de entrada de la app
    │   ├── api/            # Endpoints REST
    │   │   └── v1/
    │   │       ├── router.py       # API Router central
    │   │       └── endpoints/      # Controladores
    │   ├── core/           # Configuración del núcleo
    │   │   ├── config.py
    │   │   └── security.py # Middleware de Seguridad (Regla 5.4)
    │   ├── models/         # Modelos de BBDD (SQLAlchemy/SQLModel)
    │   ├── schemas/        # Modelos Pydantic (Entrada/Salida)
    │   │   └── report.py   # Esquema de Ficha Legal y Resultado
    │   ├── services/       # Lógica de negocio pura
    │   │   ├── rag_engine.py       # Motor de búsqueda vectorial
    │   │   └── pdf_generator.py    # "Paquete para asesor"
    │   └── agents/         # Lógica de IA (Los "Cerebros")
    │       ├── orchestrator.py     # Router de intenciones (Tool Selection)
    │       ├── tools/
    │       │   ├── viability.py    # Herramienta 1: Viabilidad (Riesgo/Ruta)
    │       │   ├── inquiry.py      # Herramienta 2: Duda puntual
    │       │   ├── briefing.py     # Herramienta 3: Preparar reunión
    │       │   └── compliance.py   # Herramienta 4: Formalización
    │       └── guardrails.py       # Validadores de salida (Safety Layer)
    └── requirements.txt
```

---

## Mapeo de Requisitos a Componentes

### 1. El Router y las Herramientas
El sistema utilizará un patrón de **Router de Intenciones** (`agents/orchestrator.py`) que analizará la entrada del usuario y delegará a uno de los agentes especializados en `agents/tools/`.

### 2. Implementación de Herramientas Específicas

#### Herramienta 1: Viabilidad (Semáforo)
- **Ubicación**: `agents/tools/viability.py`
- **Lógica**: Cadena secuencial:
    1.  Extracción de entidades (Organización, Proyecto).
    2.  Análisis de Riesgo (`services/risk_engine.py`).
    3.  Evaluación de Condiciones Mínimas.
    4.  Generación de Semáforo (Enum: `GREEN`, `YELLOW`).
    5.  Cálculo de Ruta Crítica (Roadmap).

#### Herramienta 2: Duda Puntual
- **Ubicación**: `agents/tools/inquiry.py`
- **Lógica**: RAG estricto. Busca en la base de conocimiento normativa. Si la confianza es baja (< umbral), activa `fallback` a asesor humano no-vinculante.

#### Herramienta 3: Preparar Reunión
- **Ubicación**: `agents/tools/briefing.py`
- **Lógica**: Agregación de datos. No evalúa, solo resume y extrae preguntas clave de la conversación previa y documentos subidos.

#### Herramienta 4: Cumplimiento
- **Ubicación**: `agents/tools/compliance.py`
- **Lógica**: Sistema de Checklist (Grafo de dependencia). "Si no X -> Bloquea Y".

### 3. Regla Transversal de Seguridad (5.4)
- **Implementación**: Middleware o Decorador en `core/security.py`.
- **Función**: Intercepta la salida de cualquier agente. Si detecta afirmaciones categóricas sin el nivel de confianza adecuado o sin la "Ficha Legal Mínima", reescribe la respuesta a modo condicional o bloquea la salida sugiriendo asesoría.

### 4. Paquete para Asesor
- **Implementación**: Servicio de generación de documentos (`backend/app/services/pdf_generator.py`).
- **Activación**: Automática cuando el `RiskScore` es alto o la consulta excede la capacidad del RAG.

---

## Flujo de Datos

1.  **Frontend**: Usuario envía consulta -> `useProjectEvaluation` hook.
2.  **API**: Recibe JSON.
3.  **Orquestador**: Decide si es "Consulta Puntual" o "Evaluación de Proyecto".
4.  **Agente Seleccionado**: Ejecuta lógica (LangChain graph).
5.  **Guardrails**: Verifica la respuesta final contra la Regla 5.4.
6.  **Respuesta**: Frontend recibe JSON estructurado (ej. `{ traffic_light: "YELLOW", risks: [...], next_steps: [...] }`) y renderiza la UI adecuada.
