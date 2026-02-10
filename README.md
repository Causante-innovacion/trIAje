# GPT-Legal (Causante)

Asistente legal potenciado por IA diseñado para evaluar la viabilidad de proyectos, resolver dudas normativas y preparar procesos de formalización con un enfoque en seguridad jurídica.

## Estructura del Proyecto

```
gpt-legal/
├── backend/          # API FastAPI (Python)
├── frontend/         # Aplicación React (TypeScript + Vite)
├── RAG/              # Sistema RAG con ChromaDB
├── Documentos LEGALES/  # PDFs de normativa peruana (fuente)
└── docs/             # Documentación de arquitectura
```

Para entender el diseño técnico:
- [Arquitectura del Sistema](docs/ARCHITECTURE.md)

## Tecnologias

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite, React Router, Zustand
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, ChromaDB, LangChain
- **RAG**: ChromaDB, Sentence-Transformers, LlamaParse / PyMuPDF
- **IA**: OpenAI (GPT-4o), Anthropic (Claude)

## Requisitos Previos

- **Node.js** >= 18.x y **npm** >= 9.x
- **Python** >= 3.11
- **Git**

## Instalacion y Ejecucion

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd gpt-legal
```

### 2. Backend (FastAPI)

```bash
# Ir a la carpeta del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys (ver seccion "Variables de Entorno")

# Iniciar el servidor (puerto 8000)
uvicorn app.main:app --reload --port 8000
```

El backend estara disponible en:
- API: http://localhost:8000
- Documentacion Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. Frontend (React + Vite)

```bash
# Ir a la carpeta del frontend (desde la raiz del proyecto)
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo (puerto 5173)
npm run dev
```

El frontend estara disponible en: http://localhost:5173

Para generar build de produccion:
```bash
npm run build
npm run preview   # Para previsualizar el build
```

### 4. RAG - Sistema de Busqueda Vectorial (Opcional)

El sistema RAG permite buscar en la normativa legal peruana usando busqueda semantica.

```bash
# Ir a la carpeta RAG (desde la raiz del proyecto)
cd RAG

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Para extraccion de PDFs con PyMuPDF (gratuito, recomendado):
pip install PyMuPDF

# Configurar variables de entorno
cp .env.example .env
# Agregar LLAMA_CLOUD_API_KEY si se desea usar LlamaParse
# Agregar OPENAI_API_KEY para generacion de respuestas
```

#### Procesar documentos legales y cargar a ChromaDB

```bash
# Ver documentos disponibles
python process_new_documents.py --list

# Dry run (ver que se procesaria sin ejecutar)
python process_new_documents.py --dry-run

# Procesar todos los documentos nuevos
python process_new_documents.py

# Procesar solo una categoria
python process_new_documents.py --category cooperacion
python process_new_documents.py --category laboral
python process_new_documents.py --category tributario
python process_new_documents.py --category propiedad_intelectual

# Procesar un documento especifico
python process_new_documents.py --doc ley_27692_apci
```

#### Verificar la base vectorial

```bash
python test_busqueda.py
```

## Variables de Entorno

### Backend (`backend/.env`)

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API key de OpenAI (requerido) | `sk-...` |
| `ANTHROPIC_API_KEY` | API key de Anthropic (opcional) | `sk-ant-...` |
| `DATABASE_URL` | URL de base de datos | `sqlite+aiosqlite:///./gpt_legal.db` |
| `CHROMA_MODE` | Modo ChromaDB: `local`, `server`, `memory` | `local` |
| `CHROMA_PERSIST_DIR` | Directorio de persistencia ChromaDB | `./chroma_data` |
| `DEBUG` | Modo debug | `true` |
| `CORS_ORIGINS` | Origenes CORS permitidos | `["http://localhost:5173"]` |

### RAG (`RAG/.env`)

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `LLAMA_CLOUD_API_KEY` | API key de LlamaParse (opcional) | `llx-...` |
| `OPENAI_API_KEY` | API key de OpenAI para generacion | `sk-...` |

### Frontend

El frontend usa variables de entorno de Vite. Crear un archivo `.env` en `frontend/`:

| Variable | Descripcion | Default |
|----------|-------------|---------|
| `VITE_API_URL` | URL del backend | `http://localhost:8000` |

## Ejecutar Tests

### Backend

```bash
cd backend

# Activar entorno virtual
# (ver instrucciones arriba)

# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app

# Un test especifico
pytest tests/test_legal_rules.py -v
```

### Frontend

```bash
cd frontend

# Type check
npx tsc --noEmit

# Build (incluye type check)
npm run build
```

## Dependencias Principales

### Backend (`backend/requirements.txt`)

| Paquete | Uso |
|---------|-----|
| `fastapi` | Framework web async |
| `uvicorn` | Servidor ASGI |
| `pydantic` | Validacion de datos |
| `openai` | Integracion con GPT |
| `anthropic` | Integracion con Claude |
| `chromadb` | Base de datos vectorial |
| `langchain` | Framework RAG |
| `sentence-transformers` | Embeddings locales |
| `python-dotenv` | Variables de entorno |
| `pytest` | Testing |

### Frontend (`frontend/package.json`)

| Paquete | Uso |
|---------|-----|
| `react` / `react-dom` | UI framework |
| `react-router-dom` | Navegacion SPA |
| `axios` | Cliente HTTP |
| `zustand` | Estado global |
| `lucide-react` | Iconos |
| `clsx` | Utilidad de clases CSS |
| `tailwindcss` | Framework CSS |
| `typescript` | Tipado estatico |
| `vite` | Bundler y dev server |

### RAG (`RAG/requirements.txt`)

| Paquete | Uso |
|---------|-----|
| `llama-parse` | Extraccion de texto de PDFs (API) |
| `PyMuPDF` | Extraccion de texto de PDFs (local, gratuito) |
| `langchain` | Framework RAG |
| `chromadb` | Base de datos vectorial |
| `sentence-transformers` | Modelo de embeddings multilingue |
| `torch` | Backend ML para embeddings |
| `python-dotenv` | Variables de entorno |

## Inicio Rapido (TL;DR)

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv && venv\Scripts\activate.bat
pip install -r requirements.txt
cp .env.example .env
# Editar .env con OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Abrir http://localhost:5173 en el navegador.
