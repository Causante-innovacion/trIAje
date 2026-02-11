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
# Asegúrate de que requirements.txt está en la misma carpeta que este Dockerfile
COPY requirements.txt .

# 5. Instalamos las librerías de Python
# Agregamos --no-cache-dir para mantener la imagen ligera
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos todo el resto del código a la caja
COPY . .

# 7. Abrimos una ventanita (puerto) para que pueda hablar hacia afuera
EXPOSE 8000

# 8. ¡A cocinar! (Comando para encender el servidor)
# Usamos uvicorn directamente como en la guía
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]