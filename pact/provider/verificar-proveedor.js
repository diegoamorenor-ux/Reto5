/**
 * FASE 5 — Verificación del Proveedor con Pact (Lado Provider: api-tienda).
 *
 * Lee el contrato generado por el Consumer (pact/pacts/front-tienda-api-tienda.json)
 * y reproduce cada una de sus interacciones contra la API real (Provider: api-tienda)
 * corriendo en BASE_URL (por defecto http://localhost:3000).
 *
 * Verifica para cada interacción:
 *   1. Código de estado HTTP exacto (200, 201)
 *   2. Cabeceras obligatorias (Content-Type: application/json)
 *   3. Estructura del cuerpo y reglas de coincidencia (matchingRules: tipos, regex de
 *      categorías, longitud mínima del catálogo >= 20, igualdad en campos clave).
 *
 * Sale con código 0 si el Provider cumple el 100% del contrato, o 1 si rompe el contrato.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ARCHIVO_PACT = path.resolve(__dirname, '..', 'pacts', 'front-tienda-api-tienda.json');
const ARCHIVO_REPORTE = path.resolve(__dirname, '..', 'pacts', 'verificacion-provider-resultado.json');
const PROVIDER_BASE_URL = (process.env.BASE_URL || 'http://localhost:3000').replace(/\/$/, '');

const c = {
  reset: '\x1b[0m',
  verde: '\x1b[32m',
  rojo: '\x1b[31m',
  cyan: '\x1b[36m',
  gris: '\x1b[90m',
  bold: '\x1b[1m',
};

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function validarTipoSimilar(esperado, actual, ruta) {
  if (Array.isArray(esperado)) {
    assert(Array.isArray(actual), `${ruta} debía ser un Array`);
    assert(actual.length > 0, `${ruta} no puede estar vacío`);
    validarTipoSimilar(esperado[0], actual[0], `${ruta}[0]`);
    return;
  }
  if (esperado !== null && typeof esperado === 'object') {
    assert(actual !== null && typeof actual === 'object', `${ruta} debía ser un objeto`);
    for (const k of Object.keys(esperado)) {
      assert(k in actual, `Falta el campo obligatorio "${k}" en ${ruta}`);
      validarTipoSimilar(esperado[k], actual[k], `${ruta}.${k}`);
    }
    return;
  }
  assert(
    typeof actual === typeof esperado,
    `Tipo inválido en ${ruta}: esperaba ${typeof esperado}, llegó ${typeof actual}`
  );
}

function validarMatchingRules(rules, body) {
  if (!rules) return;
  for (const [jsonPath, regla] of Object.entries(rules)) {
    if (jsonPath === '$.body' && regla.min) {
      assert(
        Array.isArray(body) && body.length >= regla.min,
        `$.body tiene ${body?.length} elementos, pero el contrato exige mínimo ${regla.min}`
      );
    }
    if (jsonPath === '$.body[*].categoria' && regla.regex) {
      const re = new RegExp(regla.regex);
      for (const item of body) {
        assert(
          re.test(item.categoria),
          `Categoría "${item.categoria}" no cumple regex del contrato ${regla.regex}`
        );
      }
    }
    if (jsonPath.startsWith('$.body.') && regla.match === 'equality') {
      const campo = jsonPath.replace('$.body.', '');
      assert(campo in body, `Campo ${campo} no existe en respuesta del Provider`);
    }
  }
}

async function verificarProveedor() {
  console.log('\n' + c.bold + '=== PACT CONTRACT TEST — FASE PROVIDER VERIFICATION (api-tienda) ===' + c.reset);
  console.log(c.gris + `  Contrato Pact   : pact/pacts/front-tienda-api-tienda.json`);
  console.log(`  Provider URL    : ${PROVIDER_BASE_URL}` + c.reset + '\n');

  if (!fs.existsSync(ARCHIVO_PACT)) {
    console.error(c.rojo + 'No existe el archivo Pact. Ejecuta primero: node pact/consumer/productos.consumer.pact.js' + c.reset);
    process.exit(1);
  }

  const pact = JSON.parse(fs.readFileSync(ARCHIVO_PACT, 'utf-8'));
  console.log(
    `  Verificando contrato entre Consumer ${c.bold}"${pact.consumer.name}"${c.reset} y Provider ${c.bold}"${pact.provider.name}"${c.reset}:\n`
  );

  let pasadas = 0;
  let falladas = 0;
  const detalleResultados = [];

  for (const ix of pact.interactions) {
    const etiqueta = `[${ix.request.method} ${ix.request.path}] — ${ix.description}`;
    try {
      console.log(c.gris + `  Given (Provider State): ${ix.providerState}` + c.reset);
      const opciones = {
        method: ix.request.method,
        headers: ix.request.headers || {},
      };
      if (ix.request.body) {
        opciones.body = JSON.stringify(ix.request.body);
      }

      const r = await fetch(PROVIDER_BASE_URL + ix.request.path, opciones);
      assert(
        r.status === ix.response.status,
        `Status HTTP esperado ${ix.response.status}, recibido ${r.status}`
      );

      const contentType = r.headers.get('content-type') || '';
      assert(
        contentType.includes('application/json'),
        `Header Content-Type inválido: ${contentType}`
      );

      const bodyActual = await r.json();
      validarTipoSimilar(ix.response.body, bodyActual, '$.body');
      validarMatchingRules(ix.response.matchingRules, bodyActual);

      // Si hay reglas de equality explícitas, compararlas contra el ejemplo del contrato
      if (ix.response.matchingRules) {
        for (const [ruta, regla] of Object.entries(ix.response.matchingRules)) {
          if (ruta.startsWith('$.body.') && regla.match === 'equality') {
            const campo = ruta.replace('$.body.', '');
            assert(
              bodyActual[campo] === ix.response.body[campo],
              `Campo ${campo}: esperaba ${JSON.stringify(ix.response.body[campo])}, llegó ${JSON.stringify(bodyActual[campo])}`
            );
          }
        }
      }

      console.log('  ' + c.verde + '✓ VERIFICADO ' + c.reset + etiqueta + '\n');
      pasadas++;
      detalleResultados.push({
        interaccion: ix.description,
        endpoint: `${ix.request.method} ${ix.request.path}`,
        statusEsperado: ix.response.status,
        statusRecibido: r.status,
        resultado: 'PASSED',
      });
    } catch (e) {
      console.log('  ' + c.rojo + '✗ FALLO      ' + c.reset + etiqueta + ' -> ' + e.message + '\n');
      falladas++;
      detalleResultados.push({
        interaccion: ix.description,
        endpoint: `${ix.request.method} ${ix.request.path}`,
        resultado: 'FAILED',
        error: e.message,
      });
    }
  }

  const resumen = {
    consumer: pact.consumer.name,
    provider: pact.provider.name,
    providerBaseUrl: PROVIDER_BASE_URL,
    fechaVerificacion: new Date().toISOString(),
    interaccionesTotales: pact.interactions.length,
    pasadas,
    falladas,
    estadoGlobal: falladas === 0 ? 'VERIFIED_GREEN' : 'FAILED_RED',
    detalles: detalleResultados,
  };

  fs.writeFileSync(ARCHIVO_REPORTE, JSON.stringify(resumen, null, 2), 'utf-8');

  console.log(c.bold + '====================================================================' + c.reset);
  console.log(
    `  Interacciones verificadas: ${c.verde}${pasadas}${c.reset} / ${pact.interactions.length}   Fallidas: ${
      falladas ? c.rojo : c.verde
    }${falladas}${c.reset}`
  );
  if (falladas === 0) {
    console.log(
      '  ' +
        c.verde +
        c.bold +
        'PACT PROVIDER VERIFICATION EN VERDE — El proveedor cumple el contrato' +
        c.reset
    );
  } else {
    console.log(
      '  ' + c.rojo + c.bold + 'PACT PROVIDER VERIFICATION EN ROJO — Ruptura de contrato detectada' + c.reset
    );
  }
  console.log(c.bold + '====================================================================\n' + c.reset);

  process.exit(falladas === 0 ? 0 : 1);
}

verificarProveedor();
