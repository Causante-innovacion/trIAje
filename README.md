# ⚖️ trIAje (Causante)

¡Bienvenido al repositorio oficial de **trIAje**! 

Este proyecto es un **Asistente Legal potenciado por Inteligencia Artificial (RAG)** diseñado para evaluar la viabilidad de proyectos, resolver dudas normativas y preparar procesos de formalización con un enfoque estricto en la seguridad jurídica, orientado a Organizaciones No Gubernamentales (ONGs) en Perú.

A diferencia de un chatbot genérico, este es un **Sistema Experto**. No inventa respuestas: busca información exacta en normativas vigentes (Código Civil, Reglamentos, etc.) cruzándola con explicaciones didácticas (Guías Modelo), logrando traducir el "legalese" a un lenguaje accesible sin alucinaciones.

---

## 📚 Documentación (Única Fuente de Verdad)

Para mantener este README enfocado en el "Setup" (Onboarding), toda la documentación técnica, decisiones arquitectónicas y guías detalladas viven en la carpeta `/docs/`. Si buscas el *por qué* o el *cómo* profundo, ese es tu lugar:

*   🏛️ **Arquitectura del Sistema:** Entiende cómo se comunican FastAPI, React y LangGraph. 👉 [Ir a Arquitectura Base](docs/arquitectura/sistema_base.md)
*   🧠 **Motor RAG (ChromaDB):** Cómo funciona la memoria del asistente y el NLP. 👉 [Ir a Documentación del RAG](docs/arquitectura/sistema_rag.md)
*   🚀 **Despliegue a Producción:** Cómo llevar este proyecto a un VPS con Docker (La guía del Capitán). 👉 [Ir a Guía de Despliegue](docs/setup/despliegue.md)
*   🤝 **Contratos de Datos / API:** Qué JSON envían y qué objetos esperan los componentes del sistema. 👉 *(Pronto)* [Ir a API Docs](docs/api/contratos_datos.md)
*   💡 **Decisiones de Arquitectura (ADRs):** Por qué elegimos estas tecnologías y no otras. 👉 *(Pronto)* [Ver ADRs](docs/adrs/)

---

## 🛠️ Requisitos Previos

Asegúrate de tener instaladas estas herramientas en tu sistema antes de clonar el proyecto:

*   **Node.js** (versión >= 18.x) y **npm** (versión >= 9.x)
*   **Python** (versión >= 3.11)
*   **Git**
*   *(Opcional, pero recomendado para producción)*: **Docker Desktop**

---

## 🚀 Guía Rápida de Instalación y Ejecución (Desarrollo Local)

Sigue estos pasos copiar y pegar para levantar el ecosistema completo en modo desarrollador:

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-organizacion/triaje.git
cd triaje
```

### 2. Levantar el Backend (El Cerebro)

El backend expone la API y controla la lógica de LangChain/FastAPI.

```bash
# 1. Ve a la carpeta del backend
cd backend

# 2. Crea un entorno virtual para aislar las dependencias
python -m venv venv

# 3. Activa el entorno virtual
# En Windows (PowerShell):
venv\Scripts\Activate.ps1
# En Windows (CMD):
venv\Scripts\activate.bat
# En Linux/Mac:
source venv/bin/activate

# 4. Instala las dependencias de Python
pip install -r requirements.txt

# 5. Configura tus secretos (Claves API)
cp .env.example .env
# Abre el archivo .env y agrega tu OPENAI_API_KEY (Obligatorio)

# 6. Inicia el servidor
uvicorn app.main:app --reload --port 8000
```
*✅ El backend estará vivo en `http://localhost:8000`. Puedes ver la documentación interactiva en `http://localhost:8000/docs`.*

### 3. Levantar el Frontend (La Interfaz)

Abre una **NUEVA** pestaña de terminal (no cierres el backend).

```bash
# 1. Ve a la carpeta del frontend (desde la raíz del proyecto)
cd frontend

# 2. Instala las dependencias de Node
npm install

# 3. Inicia el servidor de desarrollo de Vite
npm run dev
```
*✅ El frontend estará vivo en `http://localhost:5173`. Abre este enlace en tu navegador.*

---

## 🗄️ Variables de Entorno (Configuration)

El sistema depende de variables de entorno para funcionar. Aquí las más críticas:

### Backend (`backend/.env`)
| Variable | Descripción | Obligatorio | Ejemplo |
| :--- | :--- | :---: | :--- |
| `OPENAI_API_KEY` | Llave para el LLM principal. | Sí | `sk-proj-...` |
| `DATABASE_URL` | URL de la base de datos (por defecto SQLite). | No | `sqlite+aiosqlite:///./triaje.db` |
| `CHROMA_MODE` | Dónde vive la DB vectorial (`local`, `server`, `memory`). | No | `local` |

### Frontend (`frontend/.env`)
Vite inyectará estas variables al compilar (deben empezar con `VITE_`).
| Variable | Descripción | Default |
| :--- | :--- | :--- |
| `VITE_API_URL` | Dónde buscar al servidor backend. | `http://localhost:8000` |

---

## 🧪 Pruebas (Tests)

### Backend
Para verificar que la lógica de negocio esté sana:
```bash
cd backend
# Asegúrate de tener el entorno virtual activado
pytest
```

---

## 🤝 ¿Cómo Contribuir?
Este proyecto es de código abierto. Si detectas fallos en la lógica legal, vacíos normativos en el RAG, o simplemente tienes ideas para optimizar el Frontend:
1. Revisa [Nuestra Arquitectura](docs/arquitectura/sistema_base.md) para entender el flujo.
2. Abre un Issue descriptivo.
3. Envía un Pull Request.

> *"El código claro y bien documentado no es un lujo, es una necesidad de supervivencia."*
> — *The Scribe*
