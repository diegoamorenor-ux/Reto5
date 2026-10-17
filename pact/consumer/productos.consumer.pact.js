/**
 * FASE 5 — Contract Testing con Pact (Lado Consumer: front-tienda).
 *
 * Implementa el test de contrato impulsado por el consumidor (Consumer-Driven Contract)
 * entre el Frontend SPA (consumer: "front-tienda") y el Backend API (provider: "api-tienda"):
 *   1. Levanta un servidor Mock de Pact local en un puerto efímero.
 *   2. Registra las expectativas (interactions) del Front sobre:
 *      - GET /api/productos (catálogo de productos con id, nombre, categoria, precio, stock)
 *      - GET /api/productos/1 (detalle de un producto individual)
 *      - POST /api/pedidos (creación de un pedido desde el checkout del carrito)
 *   3. Ejecuta las funciones reales de consumo HTTP del cliente contra el Mock Server.
 *   4. Valida que todas las interacciones se cumplieron y genera el archivo de contrato
 *      estándar Pact Specification v2.0.0 en:
 *        pact/pacts/front-tienda-api-tienda.json
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RUTA_PACTS = path.resolve(__dirname, '..', 'pacts');
const ARCHIVO_PACT = path.join(RUTA_PACTS, 'front-tienda-api-tienda.json');

const c = {
  reset: '\x1b[0m',
  verde: '\x1b[32m',
  rojo: '\x1b[31m',
  cyan: '\x1b[36m',
  amarillo: '\x1b[33m',
  gris: '\x1b[90m',
  bold: '\x1b[1m',
};

// Definición formal de las interacciones del contrato (Pact v2.0.0)
const interacciones = [
  {
    description: 'una solicitud GET para obtener la lista del catalogo de productos',
    providerState: 'existen al menos 20 productos en el catalogo generados con Faker',
    request: {
      method: 'GET',
      path: '/api/productos',
      headers: {
        Accept: 'application/json',
      },
    },
    response: {
      status: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: [
        {
          id: 1,
          nombre: 'Licensed Cotton Shoes',
          categoria: 'hogar',
          precio: 374.29,
          descripcion: 'Ergonomic executive chair upholstered in bonded black leather',
          stock: 25,
        },
      ],
      matchingRules: {
        '$.body': { min: 20, match: 'type' },
        '$.body[*].id': { match: 'type' },
        '$.body[*].nombre': { match: 'type' },
        '$.body[*].categoria': { match: 'regex', regex: '^(hogar|tecnologia|ropa|juguetes)$' },
        '$.body[*].precio': { match: 'type' },
        '$.body[*].descripcion': { match: 'type' },
        '$.body[*].stock': { match: 'type' },
      },
    },
  },
  {
    description: 'una solicitud GET para consultar el detalle del producto con id 1',
    providerState: 'el producto con id 1 existe en el catalogo',
    request: {
      method: 'GET',
      path: '/api/productos/1',
      headers: {
        Accept: 'application/json',
      },
    },
    response: {
      status: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: {
        id: 1,
        nombre: 'Licensed Cotton Shoes',
        categoria: 'hogar',
        precio: 374.29,
        descripcion: 'Ergonomic executive chair upholstered in bonded black leather',
        stock: 25,
      },
      matchingRules: {
        '$.body.id': { match: 'equality' },
        '$.body.nombre': { match: 'type' },
        '$.body.categoria': { match: 'type' },
        '$.body.precio': { match: 'type' },
        '$.body.descripcion': { match: 'type' },
        '$.body.stock': { match: 'type' },
      },
    },
  },
  {
    description: 'una solicitud POST para confirmar un pedido desde el carrito',
    providerState: 'el producto con id 1 tiene stock disponible',
    request: {
      method: 'POST',
      path: '/api/pedidos',
      headers: {
        'Content-Type': 'application/json',
      },
      body: {
        productoId: 1,
        cliente: 'ana@tienda-qa.com',
        cantidad: 2,
      },
    },
    response: {
      status: 201,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: {
        id: 1,
        productoId: 1,
        cliente: 'ana@tienda-qa.com',
        cantidad: 2,
        total: 748.58,
        estado: 'pendiente',
        creado: '2026-10-17T14:00:00.000Z',
      },
      matchingRules: {
        '$.body.id': { match: 'type' },
        '$.body.productoId': { match: 'equality' },
        '$.body.cliente': { match: 'equality' },
        '$.body.cantidad': { match: 'equality' },
        '$.body.total': { match: 'type' },
        '$.body.estado': { match: 'equality' },
        '$.body.creado': { match: 'type' },
      },
    },
  },
];

// Cliente HTTP del Consumer (simula las funciones fetch del Front en public/index.html)
class ClienteFrontTienda {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async obtenerProductos() {
    const r = await fetch(`${this.baseUrl}/api/productos`, {
      headers: { Accept: 'application/json' },
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }

  async obtenerDetalleProducto(id) {
    const r = await fetch(`${this.baseUrl}/api/productos/${id}`, {
      headers: { Accept: 'application/json' },
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }

  async confirmarPedido(productoId, cliente, cantidad) {
    const r = await fetch(`${this.baseUrl}/api/pedidos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productoId, cliente, cantidad }),
    });
    if (r.status !== 201) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }
}

async function ejecutarConsumerPactTest() {
  console.log('\n' + c.bold + '=== PACT CONTRACT TEST — FASE CONSUMER (front-tienda -> api-tienda) ===' + c.reset);

  const invocaciones = new Set();

  // Levantar Pact Mock Server local
  const servidorMock = http.createServer(async (req, res) => {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const bodyTexto = Buffer.concat(chunks).toString('utf-8');

    const ix = interacciones.find(
      (i) => i.request.method === req.method && i.request.path === req.url
    );

    if (!ix) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: `Interacción no registrada en Pact Mock: ${req.method} ${req.url}` }));
      return;
    }

    if (ix.request.body) {
      const recibido = JSON.parse(bodyTexto || '{}');
      if (JSON.stringify(recibido) !== JSON.stringify(ix.request.body)) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Payload del Consumer no coincide con la interacción Pact' }));
        return;
      }
    }

    invocaciones.add(ix.description);
    res.writeHead(ix.response.status, ix.response.headers);
    res.end(JSON.stringify(ix.response.body));
  });

  await new Promise((resolve) => servidorMock.listen(0, '127.0.0.1', resolve));
  const puertoMock = servidorMock.address().port;
  const mockUrl = `http://127.0.0.1:${puertoMock}`;
  console.log(c.gris + `  Pact Mock Server activo en: ${mockUrl}` + c.reset + '\n');

  const cliente = new ClienteFrontTienda(mockUrl);

  try {
    // 1. Probar GET /api/productos en el Consumer
    const lista = await cliente.obtenerProductos();
    if (!Array.isArray(lista) || typeof lista[0].precio !== 'number') {
      throw new Error('El Consumer no pudo procesar la lista de productos');
    }
    console.log('  ' + c.verde + '✓ PASS ' + c.reset + 'Consumer: GET /api/productos procesa catálogo y formatea precios ($' + lista[0].precio.toFixed(2) + ')');

    // 2. Probar GET /api/productos/1 en el Consumer
    const detalle = await cliente.obtenerDetalleProducto(1);
    if (detalle.id !== 1 || !detalle.nombre) {
      throw new Error('El Consumer no pudo procesar el detalle del producto 1');
    }
    console.log('  ' + c.verde + '✓ PASS ' + c.reset + 'Consumer: GET /api/productos/1 procesa vista de detalle (' + detalle.nombre + ')');

    // 3. Probar POST /api/pedidos en el Consumer
    const pedido = await cliente.confirmarPedido(1, 'ana@tienda-qa.com', 2);
    if (pedido.estado !== 'pendiente' || typeof pedido.id !== 'number') {
      throw new Error('El Consumer no recibió confirmación válida del pedido');
    }
    console.log('  ' + c.verde + '✓ PASS ' + c.reset + 'Consumer: POST /api/pedidos recibe orden #' + pedido.id + ' en estado "' + pedido.estado + '"');

    if (invocaciones.size !== interacciones.length) {
      throw new Error(`Faltaron interacciones por verificar (${invocaciones.size}/${interacciones.length})`);
    }

    // Escribir el contrato Pact JSON
    const contratoPact = {
      consumer: { name: 'front-tienda' },
      provider: { name: 'api-tienda' },
      interactions: interacciones,
      metadata: {
        pactSpecification: { version: '2.0.0' },
        client: { name: 'pact-js-lightweight', version: '1.0.0' },
      },
    };

    fs.mkdirSync(RUTA_PACTS, { recursive: true });
    fs.writeFileSync(ARCHIVO_PACT, JSON.stringify(contratoPact, null, 2), 'utf-8');

    console.log('\n  ' + c.cyan + '📄 Contrato Pact generado exitosamente en:' + c.reset);
    console.log('     ' + c.bold + 'pact/pacts/front-tienda-api-tienda.json' + c.reset);
    console.log('  ' + c.verde + c.bold + 'CONSUMER PACT TEST EN VERDE (3/3 interacciones verificadas)' + c.reset + '\n');
  } finally {
    servidorMock.close();
  }
}

ejecutarConsumerPactTest().catch((err) => {
  console.error(c.rojo + 'Fallo en Consumer Pact Test: ' + err.message + c.reset);
  process.exit(1);
});
