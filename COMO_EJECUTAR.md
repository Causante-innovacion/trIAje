# 🚀 Cómo Ejecutar el Proyecto GPT Legal

## 📋 Resumen Rápido

Este proyecto tiene **dos partes** que deben ejecutarse simultáneamente:
- **Backend** (Python/FastAPI) - Puerto 8000
- **Frontend** (React/Vite) - Puerto 5173

---

## ⚙️ Instalación Inicial (Solo la primera vez)

### 1. Backend (Python)
```powershell
# Crear entorno virtual
python -m venv backend\venv

# Activar entorno virtual
backend\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r backend\requirements.txt
```

### 2. Frontend (Node.js)
```powershell
cd frontend
npm install
cd ..
```

---

## 🏃 Ejecución Diaria (Cada vez que trabajes en el proyecto)

### Necesitas DOS terminales abiertas simultáneamente

#### Terminal 1: Backend
```powershell
# Navegar a la carpeta backend
cd backend

# Activar el entorno virtual (SIEMPRE necesario)
.\venv\Scripts\Activate.ps1

# Iniciar el servidor FastAPI
uvicorn app.main:app --reload
```

**Verás algo como:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

✅ **Backend corriendo en:** http://localhost:8000

---

#### Terminal 2: Frontend
```powershell
# Navegar a la carpeta frontend
cd frontend

# Iniciar el servidor de desarrollo
npm run dev
```

**Verás algo como:**
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

✅ **Frontend corriendo en:** http://localhost:5173

---

## 🌐 Acceder a la Aplicación

Una vez que ambos servidores estén corriendo:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Aplicación Web** | http://localhost:5173 | Interfaz de usuario principal |
| **API Docs (Swagger)** | http://localhost:8000/docs | Documentación interactiva de la API |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | Documentación alternativa |

---

## ❓ Preguntas Frecuentes

### ¿Por qué tengo que activar el entorno virtual cada vez?

El entorno virtual de Python (`venv`) **no es permanente**. Cada vez que:
- Abres una nueva terminal
- Reinicias Antigravity/VS Code
- Reinicias tu computadora

Necesitas volver a activar el entorno virtual con:
```powershell
backend\venv\Scripts\Activate.ps1
```

**Sabrás que está activado** cuando veas `(venv)` al inicio de la línea de comandos:
```
(venv) PS C:\Users\User\Documents\GitHub\gpt-legal\backend>
```

---

### ¿Qué pasa si olvido activar el entorno virtual?

Si intentas ejecutar el backend sin activar el `venv`, obtendrás errores como:
```
ModuleNotFoundError: No module named 'fastapi'
```

Esto es porque el Python global de tu sistema no tiene las librerías instaladas.

**Solución:** Activa el entorno virtual y vuelve a intentar.

---

### ¿Puedo ejecutar todo en una sola línea?

Sí, puedes usar comandos combinados:

**Backend (una línea):**
```powershell
cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload
```

**Frontend (una línea):**
```powershell
cd frontend; npm run dev
```

---

### ¿Cómo detengo los servidores?

En cada terminal, presiona:
```
Ctrl + C
```

Esto detendrá el servidor de forma segura.

---

## 🔧 Configuración de Variables de Entorno (Opcional)

Para usar las funcionalidades de IA (OpenAI, Anthropic), necesitas configurar tus API keys:

### Backend
```powershell
# Copiar el archivo de ejemplo
copy backend\.env.example backend\.env

# Editar backend\.env y agregar tus API keys:
# OPENAI_API_KEY=tu_api_key_aqui
# ANTHROPIC_API_KEY=tu_api_key_aqui
```

### RAG (para scripts de procesamiento de documentos)
```powershell
# Copiar el archivo de ejemplo
copy RAG\.env.example RAG\.env

# Editar RAG\.env y agregar tu API key:
# OPENAI_API_KEY=tu_api_key_aqui
```

---

## 📁 Estructura del Proyecto

```
gpt-legal/
├── backend/              # API FastAPI (Python)
│   ├── venv/            # Entorno virtual (NO subir a Git)
│   ├── app/             # Código de la aplicación
│   ├── requirements.txt # Dependencias de Python
│   └── .env            # Variables de entorno (NO subir a Git)
│
├── frontend/            # Interfaz React (Node.js)
│   ├── node_modules/   # Dependencias de Node (NO subir a Git)
│   ├── src/            # Código fuente
│   ├── package.json    # Dependencias de Node
│   └── vite.config.ts  # Configuración de Vite
│
└── RAG/                # Sistema de base de conocimiento
    ├── chroma_db/      # Base de datos vectorial
    ├── knowledge_base/ # Documentos legales (PDFs)
    └── *.py           # Scripts de procesamiento
```

---

## 🐛 Solución de Problemas

### Error: "No se puede cargar el archivo... porque la ejecución de scripts está deshabilitada"

**Solución:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Causa:** El entorno virtual no está activado.

**Solución:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

### Error: "npm: command not found"

**Causa:** Node.js no está instalado.

**Solución:** Instala Node.js desde https://nodejs.org/

### El frontend no se conecta al backend

**Verifica:**
1. Que el backend esté corriendo en http://localhost:8000
2. Que el frontend esté corriendo en http://localhost:5173
3. Revisa la consola del navegador (F12) para ver errores

---

## 📝 Comandos de Referencia Rápida

### Backend
```powershell
# Activar entorno virtual
backend\venv\Scripts\Activate.ps1

# Iniciar servidor
uvicorn app.main:app --reload

# Instalar nueva dependencia
pip install nombre-paquete

# Actualizar requirements.txt
pip freeze > requirements.txt
```

### Frontend
```powershell
# Iniciar servidor de desarrollo
npm run dev

# Compilar para producción
npm run build

# Instalar nueva dependencia
npm install nombre-paquete
```

### RAG (Scripts de procesamiento)
```powershell
# Activar entorno virtual del backend
backend\venv\Scripts\Activate.ps1

# Probar búsqueda semántica
python RAG\test_busqueda.py

# Procesar nuevos documentos
python RAG\process_new_documents.py

# Ver ayuda de un script
python RAG\process_new_documents.py --help
```

---

## ✅ Checklist de Inicio

Cada vez que trabajes en el proyecto:

- [ ] Abrir Antigravity en la carpeta del proyecto
- [ ] Abrir Terminal 1 y ejecutar backend
  - [ ] `cd backend`
  - [ ] `.\venv\Scripts\Activate.ps1`
  - [ ] `uvicorn app.main:app --reload`
- [ ] Abrir Terminal 2 y ejecutar frontend
  - [ ] `cd frontend`
  - [ ] `npm run dev`
- [ ] Verificar que ambos servidores estén corriendo
  - [ ] Backend: http://localhost:8000/docs
  - [ ] Frontend: http://localhost:5173

---

## 🎯 Próximos Pasos

1. **Configurar variables de entorno** (`.env`) con tus API keys
2. **Probar la aplicación** en http://localhost:5173
3. **Revisar la documentación de la API** en http://localhost:8000/docs
4. **Explorar el código** en las carpetas `backend/app/` y `frontend/src/`

---

**¡Listo para desarrollar!** 🚀
