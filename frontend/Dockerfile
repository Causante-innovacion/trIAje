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
