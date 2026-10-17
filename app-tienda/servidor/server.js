/**
 * App Tienda - Proceso unificado Node/Express que sirve:
 *   - Front estático SPA (public/) : catálogo, filtros, búsqueda, detalle, carrito, checkout
 *   - API REST (/api/...)          : /api/health, /api/productos, /api/pedidos, /api/clientes, /api/test/reset
 */
import express from 'express';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(__dirname, '..');
const DB_PATH = join(RAIZ, 'datos', 'db.json');

if (!existsSync(DB_PATH)) {
  console.error('No existe datos/db.json. Ejecuta: npm run generar o node datos/generar-datos.js');
  process.exit(1);
}

const db = JSON.parse(readFileSync(DB_PATH, 'utf-8'));
let productos = db.productos;
let pedidos = db.pedidos || [];
let clientes = db.clientes || [];
let siguientePedidoId = 1;

const app = express();
app.use(express.json());
app.use(express.static(join(RAIZ, 'public')));

// ── API REST ───────────────────────────────────────────────────────
app.get('/api/health', (_req, res) => {
  res.json({
    estado: 'ok',
    servicio: 'app-tienda',
    totalProductos: productos.length,
    hora: new Date().toISOString(),
  });
});

app.get('/api/productos', (req, res) => {
  const { categoria, q } = req.query;
  let lista = productos;
  if (categoria) {
    lista = lista.filter((p) => p.categoria === String(categoria).toLowerCase());
  }
  if (q) {
    const t = String(q).toLowerCase();
    lista = lista.filter((p) => p.nombre.toLowerCase().includes(t));
  }
  res.json(lista);
});

app.get('/api/productos/:id', (req, res) => {
  const p = productos.find((x) => x.id === Number(req.params.id));
  if (!p) return res.status(404).json({ error: 'Producto no encontrado' });
  res.json(p);
});

app.get('/api/clientes', (_req, res) => {
  res.json(clientes);
});

app.post('/api/pedidos', (req, res) => {
  const { productoId, cliente, cantidad } = req.body || {};
  if (!productoId || !cliente || !cantidad) {
    return res.status(400).json({ error: 'Faltan datos: productoId, cliente, cantidad' });
  }
  if (Number(cantidad) <= 0) {
    return res.status(400).json({ error: 'La cantidad debe ser mayor que cero' });
  }
  const prod = productos.find((x) => x.id === Number(productoId));
  if (!prod) return res.status(404).json({ error: 'Producto no existe' });

  const pedido = {
    id: siguientePedidoId++,
    productoId: Number(productoId),
    cliente: String(cliente),
    cantidad: Number(cantidad),
    total: Number((prod.precio * Number(cantidad)).toFixed(2)),
    estado: 'pendiente',
    creado: new Date().toISOString(),
  };
  pedidos.push(pedido);
  res.status(201).json(pedido);
});

app.get('/api/pedidos', (_req, res) => res.json(pedidos));

// Endpoint de apoyo para pruebas E2E: reinicia los pedidos en memoria antes de cada escenario
app.post('/api/test/reset', (_req, res) => {
  pedidos = [];
  siguientePedidoId = 1;
  res.json({ ok: true });
});

// Front SPA: cualquier otra ruta devuelve public/index.html
app.get('*', (_req, res) => {
  res.sendFile(join(RAIZ, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log('\n==============================================');
  console.log('  App Tienda corriendo');
  console.log(`  Front : http://localhost:${PORT}/`);
  console.log(`  API   : http://localhost:${PORT}/api/productos`);
  console.log(`  Salud : http://localhost:${PORT}/api/health`);
  console.log('==============================================\n');
});
