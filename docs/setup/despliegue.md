# 🚀 Guía Maestra de Despliegue: trIAje

¡Bienvenido, Capitán de Despliegue! 👨‍✈️👩‍✈️

Esta guía es tu mapa del tesoro para llevar **trIAje** desde tu computadora ("en local") hasta un servidor real ("producción") usando la magia de los contenedores **Docker**.

No necesitas ser un experto en DevOps. Solo sigue los pasos. 😉

---

## 🎯 El Objetivo

Esta guía es tu mapa del tesoro para llevar **trIAje** desde tu computadora ("en local") hasta un servidor real ("producción") usando la magia de los contenedores **Docker**. 

La meta: Que cualquier ONG pueda tener **trIAje** vivo y conectado a internet en menos de 30 minutos.
 😉

---

## 🗺️ Mapa de la Misión

Vamos a construir 3 "cajas" (contenedores) que vivirán felices en tu servidor:
1.  🐍 **Backend**: El cerebro (Python + FastAPI).
2.  🎨 **Frontend**: La cara bonita (React + Nginx).
3.  🧠 **ChromaDB**: La memoria a largo plazo (Base de datos vectorial).

---

## 🛠️ Herramientas Necesarias

Antes de zarpar, confirma que tienes esto instalado:
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Si estás en Windows/Mac)
*   [Git](https://git-scm.com/) (Obvio, ¿no?)

---

## 🏗️ Paso 1: Preparar el Backend (La "Receta" de Python)

El archivo `Dockerfile` es como una receta de cocina. Le dice a la computadora: *"Toma estos ingredientes (código) y cocínalos así"*.

1.  Ve a la carpeta `backend/`.
2.  Crea un archivo nuevo llamado `Dockerfile` (¡Ojo! Sin extensión .txt ni nada).
3.  Copia y pega esta receta mágica:

```dockerfile
# backend/Dockerfile

# 1. Usamos una base ligera de Python (como comprar la masa de pizza hecha)
FROM python:3.11-slim

# 2. Creamos una carpeta de trabajo dentro de la caja
WORKDIR /app

# 3. Instalamos herramientas básicas de Linux (el cuchillo y el tenedor)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiamos la lista de ingredientes (requirements.txt)
COPY requirements.txt .

# 5. Instalamos las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos todo el resto del código a la caja
COPY . .

# 7. Abrimos una ventanita (puerto) para que pueda hablar hacia afuera
EXPOSE 8000

# 8. ¡A cocinar! (Comando para encender el servidor)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🎨 Paso 2: Preparar el Frontend (La "Receta" de React)

Aquí haremos algo especial: una "Construcción en 2 Etapas". Primero cocinamos la app (build) y luego la servimos en un plato elegante (Nginx).

1.  Ve a la carpeta `frontend/`.
2.  Crea otro archivo `Dockerfile`.
3.  Pega esto:

```dockerfile
# frontend/Dockerfile

# --- ETAPA 1: EL COCINERO (Node.js) ---
FROM node:20-alpine as build
WORKDIR /app

# Primero las dependencias (para aprovechar la caché de Docker y ir rápido)
COPY package.json package-lock.json ./
RUN npm install

# Ahora sí, cocinamos el código fuente
COPY . .
RUN npm run build
# (Al terminar esto, tendremos una carpeta 'dist' con la web lista)

# --- ETAPA 2: EL MESERO (Nginx) ---
FROM nginx:alpine

# Tomamos solo la carpeta 'dist' del Cocinero y la ponemos en el plato del Mesero
COPY --from=build /app/dist /usr/share/nginx/html

# Le damos instrucciones al Mesero de cómo servir (configuración)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

4.  **¡Falta un detalle!** El Mesero necesita instrucciones. Crea un archivo `nginx.conf` en la carpeta `frontend/`:

```nginx
# frontend/nginx.conf
server {
    listen 80;

    # Si alguien pide la web, dale el index.html
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Si alguien pide /api, envíalo a la caja del Backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🎼 Paso 3: El Director de Orquesta (Docker Compose)

Ahora necesitamos un archivo que haga que todas las cajas funcionen juntas y se hablen entre sí.

1.  Ve a la **raíz de todo el proyecto** (fuera de backend/frontend).
2.  Crea un archivo llamado `docker-compose.yml`.
3.  Este es el plan maestro:

```yaml
version: '3.8'

services:
  # 🐍 LA CAJA DEL BACKEND
  backend:
    build: ./backend              # Construye usando la receta de la carpeta backend
    container_name: triaje_backend
    ports:
      # - "8000:8000"             # 🔒 COMENTADO POR SEGURIDAD EN PRODUCCIÓN
                                  # Solo descomenta si necesitas probar el backend directo (Swagger)
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/triaje.db
      - CHROMA_MODE=server
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend_data:/app/data  
    depends_on:
      - chromadb
    restart: unless-stopped

  # 🎨 LA CAJA DEL FRONTEND
  frontend:
    build: ./frontend
    container_name: triaje_frontend
    ports:
      - "5173:80"                 # 🌍 ESTE ES EL ÚNICO PUERTO PÚBLICO
    depends_on:
      - backend
    restart: unless-stopped

  # 🧠 LA CAJA DE LA MEMORIA (ChromaDB)
  chromadb:
    image: chromadb/chroma:latest
    container_name: triaje_chromadb
    ports:
      # - "8001:8000"             # 🔒 CERRADO POR SEGURIDAD. Solo el Backend debe hablar con él.
    volumes:
      - chromadb_data:/chroma/chroma 
    environment:
      - IS_PERSISTENT=TRUE
    restart: unless-stopped

  # 👁️ EL VISOR DE MEMORIA (Bonus Track)
  chroma-ui:
    image: ghcr.io/chroma-core/chroma-ui:latest
    container_name: triaje_chroma_ui
    ports:
      - "3000:3000"               # 🔓 ABIERTO PARA DESARROLLO (Cerrar en producción final)
    environment:
      - CHROMA_URL=http://chromadb:8000
    depends_on:
      - chromadb
    restart: unless-stopped

# Aquí definimos los volúmenes persistentes
volumes:
  chromadb_data:
```

---

## 🚀 Paso 4: ¡A Volar en Local!

1.  **Crea el secreto:** En la raíz del proyecto, crea un archivo `.env` (si no existe) y pon tu clave:
    ```ini
    OPENAI_API_KEY=sk-tu-clave-secreta-de-openai
    ```
2.  **Lanza los cohetes:** Abre la terminal en la raíz y escribe:

    ```bash
    docker-compose up --build -d
    ```

3.  **Comprueba tus dominios:**
    *   🌍 Web App: http://localhost:5173

---

## 🔒 Paso 5: Estrategia de Puertos (Modo Seguridad)

Cuando estés trabajando en el proyecto (Desarrollo), querrás tener todos los puertos abiertos para probar. Pero cuando esto sea "público" (Producción), hay que cerrar las puertas traseras.

### 🟢 Modo Desarrollo (Todo Abierto)
Usa el `docker-compose.yml` tal cual. Te permite ver la documentación del Backend (`:8000`) y el visor de la BD (`:3000` y `:8001`).

### � Modo Producción Real (Blindado)
Cuando ya nadie tenga que tocar el código, **edita el `docker-compose.yml`** y pon un `#` delante de los puertos que no sean el Frontend.

**Ejemplo de cómo cerrar un puerto:**

```yaml
  backend:
    # ...
    ports:
      # - "8000:8000"  <-- ¡Comentado! Ahora nadie puede atacar tu API directamente.
                       # Solo el frontend (que vive dentro de la red docker) podrá hablar con él.
```

**Puertos que deberías cerrar en producción:**
1.  `8000:8000` (Backend directo): Ciérralo. Obliga a todo el tráfico a entrar por el Frontend.
2.  `8001:8000` (ChromaDB directo): ¡Ciérralo SIEMPRE! No quieres que nadie borre tu base de conocimientos.
3.  `3000:3000` (Chroma UI): Ciérralo cuando termines de revisar los datos.

---

## 🐳 Paso 6: Despliegue en Portainer

1.  Abre tu Portainer.
2.  Ve a **Stacks** ➡️ **Add stack**.
3.  Ponle nombre: `triaje`.
4.  Elige **"Repository"** y pega tu URL de GitHub.
5.  **Environment variables:** Agrega `OPENAI_API_KEY`.
6.  **¡Deploy!**

### 💡 Pro-Tip para Portainer
Si quieres cerrar un puerto temporalmente sin editar el código en GitHub:
1.  En el Stack de Portainer, ve a la pestaña **"Editor"**.
2.  Pon el `#` delante del puerto que quieras cerrar.
3.  Dale a **Update the stack**.
¡Listo! Puerta cerrada en 5 segundos. 🚪🔒

---
✨ **¡Felicidades!** Ya eres un DevOps oficial de trIAje.
