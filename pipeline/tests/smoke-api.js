/**
 * FASE 2 — Smoke Test de la API y Front de App Tienda (Quality Gate 1).
 *
 * Valida rápidamente que la aplicación "encendió" tras el build/deploy:
 *   1. GET /api/health responde 200 y estado 'ok'
 *   2. GET /api/productos devuelve catálogo poblado (24 productos con Faker)
 *   3. GET /api/productos/1 devuelve campos coherentes (id, nombre, precio, stock, categoria)
 *   4. GET /api/productos/9999 responde 404
 *   5. GET /api/productos?categoria=hogar filtra exclusivamente esa categoría
 *   6. GET / (Front SPA) responde 200 y entrega el HTML de Tienda QA
 *   7. POST /api/pedidos crea un pedido válido y responde 201 con estado 'pendiente'
 *
 * Actúa como Quality Gate: devuelve código de salida 0 si todo pasa, o 1 si falla
 * (deteniendo inmediatamente el pipeline en Azure Pipelines).
 */
const BASE = (process.env.BASE_URL || 'http://localhost:3000').replace(/\/$/, '');

const c = {
  reset: '\x1b[0m',
  verde: '\x1b[32m',
  rojo: '\x1b[31m',
  cyan: '\x1b[36m',
  gris: '\x1b[90m',
  bold: '\x1b[1m',
};

let pasadas = 0;
let falladas = 0;

async function check(nombre, fn) {
  try {
    await fn();
    console.log('  ' + c.verde + '✓ OK   ' + c.reset + nombre);
    pasadas++;
  } catch (e) {
    console.log('  ' + c.rojo + '✗ FALLO ' + c.reset + nombre + c.gris + ' -> ' + e.message + c.reset);
    falladas++;
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

async function main() {
  console.log('\n' + c.bold + '=== QUALITY GATE 1: SMOKE TEST — API & Front Tienda ===' + c.reset);
  console.log(c.gris + 'Base URL: ' + BASE + c.reset + '\n');

  // 1) Salud del servicio
  await check('GET /api/health responde 200 y estado "ok"', async () => {
    const r = await fetch(BASE + '/api/health');
    assert(r.status === 200, 'esperaba 200, llegó ' + r.status);
    const j = await r.json();
    assert(j.estado === 'ok', 'estado no es ok: ' + JSON.stringify(j));
  });

  // 2) Catálogo devuelve 20+ productos (24 generados con Faker)
  await check('GET /api/productos devuelve catálogo con 20+ productos (Faker seed 12345)', async () => {
    const r = await fetch(BASE + '/api/productos');
    assert(r.status === 200, 'esperaba 200, llegó ' + r.status);
    const j = await r.json();
    assert(Array.isArray(j), 'la respuesta no es un array');
    assert(j.length >= 20, 'esperaba al menos 20 productos, llegaron ' + j.length);
  });

  // 3) Producto individual tiene campos coherentes
  await check('GET /api/productos/1 tiene id, nombre, precio, stock y categoria', async () => {
    const r = await fetch(BASE + '/api/productos/1');
    assert(r.status === 200, 'esperaba 200, llegó ' + r.status);
    const p = await r.json();
    assert(p.id === 1, 'id incorrecto');
    assert(typeof p.nombre === 'string' && p.nombre.length > 0, 'nombre vacío');
    assert(typeof p.precio === 'number' && p.precio > 0, 'precio inválido');
    assert(typeof p.stock === 'number' && p.stock >= 0, 'stock inválido');
    assert(typeof p.categoria === 'string' && p.categoria.length > 0, 'categoría vacía');
  });

  // 4) Producto inexistente -> 404
  await check('GET /api/productos/9999 responde 404 Not Found', async () => {
    const r = await fetch(BASE + '/api/productos/9999');
    assert(r.status === 404, 'esperaba 404, llegó ' + r.status);
  });

  // 5) Filtro por categoría
  await check('GET /api/productos?categoria=hogar devuelve solo categoría "hogar"', async () => {
    const r = await fetch(BASE + '/api/productos?categoria=hogar');
    assert(r.status === 200, 'esperaba 200, llegó ' + r.status);
    const j = await r.json();
    assert(j.length > 0, 'no devolvió productos de hogar');
    assert(j.every((p) => p.categoria === 'hogar'), 'hay productos de otra categoría');
  });

  // 6) El front carga (home)
  await check('GET / (Front SPA) responde 200 y contiene "Tienda QA"', async () => {
    const r = await fetch(BASE + '/');
    assert(r.status === 200, 'esperaba 200, llegó ' + r.status);
    const html = await r.text();
    assert(html.includes('Tienda QA'), 'el HTML no corresponde a Tienda QA');
  });

  // 7) Crear un pedido válido -> 201
  await check('POST /api/pedidos con datos válidos responde 201 y estado "pendiente"', async () => {
    const r = await fetch(BASE + '/api/pedidos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productoId: 1, cliente: 'smoke@tienda-qa.com', cantidad: 1 }),
    });
    assert(r.status === 201, 'esperaba 201, llegó ' + r.status);
    const p = await r.json();
    assert(p.estado === 'pendiente', 'el pedido no nació pendiente');
    assert(typeof p.id === 'number', 'el pedido no tiene id numérico');
  });

  console.log('\n' + c.bold + '========================================================' + c.reset);
  console.log(
    '  Pasadas: ' +
      c.verde +
      pasadas +
      c.reset +
      '   Falladas: ' +
      (falladas ? c.rojo : c.verde) +
      falladas +
      c.reset
  );
  if (falladas === 0) {
    console.log('  ' + c.verde + c.bold + 'QUALITY GATE 1 (SMOKE) EN VERDE — La app encendió correctamente' + c.reset);
  } else {
    console.log('  ' + c.rojo + c.bold + 'QUALITY GATE 1 (SMOKE) EN ROJO — Deteniendo el pipeline (exit 1)' + c.reset);
  }
  console.log(c.bold + '========================================================' + c.reset + '\n');

  process.exit(falladas === 0 ? 0 : 1);
}

main().catch((e) => {
  console.error('\n' + c.rojo + 'Error crítico ejecutando smoke test: ' + e.message + c.reset);
  process.exit(1);
});
