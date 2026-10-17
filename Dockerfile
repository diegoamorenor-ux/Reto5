# ============================================================
# Dockerfile - App Tienda (Front SPA + API REST + Datos Faker)
# ------------------------------------------------------------
# Imagen ligera basada en Node 20 Alpine. Construye la app en un solo
# contenedor que genera los datos sintéticos con Faker (semilla fija)
# y expone tanto el Front como la API en el puerto 3000 con /api/health
# configurado como HEALTHCHECK nativo de Docker.
#
# Construir desde la raíz:  docker build -t app-tienda:v1 .
# Correr contenedor:        docker run -d --name tienda-qa -p 3000:3000 app-tienda:v1
# ============================================================
FROM node:20-alpine

WORKDIR /app

# 1) Copiar manifiestos primero para aprovechar la caché de capas de Docker
COPY app-tienda/package*.json ./

# 2) Copiar los scripts de generación de datos y anonimización antes de npm install
COPY app-tienda/datos ./datos

# 3) Instalar dependencias de producción (postinstall ejecuta la generación de datos)
RUN npm install --omit=dev

# 4) Copiar el resto de la aplicación (servidor Express + front estático)
COPY app-tienda/ .

# 5) Regenerar datos deterministas con Faker (semilla fija 12345)
RUN node datos/1-generar-dump-real.js && node datos/2-anonimizar.js && node datos/generar-datos.js

ENV PORT=3000
EXPOSE 3000

# 6) Healthcheck nativo contra /api/health
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "servidor/server.js"]
