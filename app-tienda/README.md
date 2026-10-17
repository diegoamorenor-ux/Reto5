# App Tienda — E-Commerce Bajo Prueba (Reto 5)

Aplicación monolítica ligera (Node.js + Express + SPA Vanilla JS) diseñada para validar las 6 fases del **Reto 5: QA Cloud-Native con IA Generativa**.

## Endpoints de la API REST

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Healthcheck del servicio (`{ estado: "ok", servicio: "app-tienda", totalProductos: 24, hora: "..." }`) |
| `GET` | `/api/productos` | Lista los 24 productos generados con Faker (semilla fija `12345`). Soporta filtros `?categoria=hogar` y `?q=texto` |
| `GET` | `/api/productos/:id` | Devuelve el detalle de un producto por su ID o `404 Not Found` |
| `GET` | `/api/clientes` | Devuelve los 15 clientes anonimizados bajo estándar GDPR (Reto Extra Fase 1) |
| `POST` | `/api/pedidos` | Crea un nuevo pedido (`{ productoId, cliente, cantidad }`) y responde `201 Created` |
| `GET` | `/api/pedidos` | Lista los pedidos creados en la sesión actual |
| `POST` | `/api/test/reset` | Endpoint de soporte E2E que reinicia la lista de pedidos en memoria antes de cada escenario |

## Comandos

```bash
# Instalar dependencias y generar datos automáticamente (postinstall)
npm install

# Regenerar el dump simulado, anonimizar PII y crear datos/db.json con semilla fija 12345
npm run generar

# Iniciar el servidor en http://localhost:3000
npm start
```
