# ============================================================
# Dockerfile - App Tienda (ejecutado dentro de app-tienda/)
# ============================================================
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
COPY datos ./datos

RUN npm install --omit=dev

COPY . .

RUN node datos/1-generar-dump-real.js && node datos/2-anonimizar.js && node datos/generar-datos.js

ENV PORT=3000
EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "servidor/server.js"]
