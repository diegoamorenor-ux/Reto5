/**
 * FASE 2 — Prueba de Carga y Quality Gate de Rendimiento (SLA).
 *
 * Lanza N usuarios virtuales concurrentes durante DURACION_S segundos contra la API
 * y calcula métricas reales de rendimiento:
 *   - Throughput (req/s)
 *   - Latencia mediana (p50) y percentil 95 (p95) en ms
 *   - Tasa de error (%)
 *
 * Evalúa el SLA exigido en el reto:
 *   - Latencia p95 < 800 ms (configurable vía SLA_P95_MS para forzar el gate en ROJO)
 *   - Tasa de error < 1%    (configurable vía SLA_ERROR_PCT)
 *
 * Si alguna condición del SLA no se cumple, finaliza con process.exit(1),
 * actuando como Quality Gate que detiene el despliegue en Azure Pipelines.
 */
const BASE = (process.env.BASE_URL || 'http://localhost:3000').replace(/\/$/, '');
const CONCURRENCIA = Number(process.env.CONCURRENCIA || 15);
const DURACION_S = Number(process.env.DURACION_S || 5);
const SLA_P95_MS = Number(process.env.SLA_P95_MS || 800);
const SLA_ERROR_PCT = Number(process.env.SLA_ERROR_PCT || 1);
const RUTA = process.env.RUTA || '/api/productos';

const c = {
  reset: '\x1b[0m',
  verde: '\x1b[32m',
  rojo: '\x1b[31m',
  cyan: '\x1b[36m',
  gris: '\x1b[90m',
  bold: '\x1b[1m',
  amarillo: '\x1b[33m',
};

const latencias = [];
let ok = 0;
let errores = 0;
let corriendo = true;

async function unaPeticion() {
  const t0 = performance.now();
  try {
    const r = await fetch(BASE + RUTA);
    const dt = performance.now() - t0;
    latencias.push(dt);
    if (r.ok) ok++;
    else errores++;
    await r.text();
  } catch {
    errores++;
    latencias.push(performance.now() - t0);
  }
}

async function usuarioVirtual() {
  while (corriendo) {
    await unaPeticion();
  }
}

function percentil(arr, p) {
  if (arr.length === 0) return 0;
  const ordenado = [...arr].sort((a, b) => a - b);
  const idx = Math.ceil((p / 100) * ordenado.length) - 1;
  return ordenado[Math.max(0, idx)];
}

async function main() {
  console.log('\n' + c.bold + '=== QUALITY GATE 2: PRUEBA DE CARGA — API Tienda ===' + c.reset);
  console.log(c.gris + 'Endpoint     : ' + BASE + RUTA);
  console.log('Concurrencia : ' + CONCURRENCIA + ' usuarios virtuales');
  console.log('Duración     : ' + DURACION_S + ' s');
  console.log('SLA exigido  : p95 < ' + SLA_P95_MS + ' ms  y  error < ' + SLA_ERROR_PCT + '%' + c.reset + '\n');

  try {
    const r = await fetch(BASE + '/api/health');
    if (!r.ok) throw new Error('health status ' + r.status);
  } catch {
    console.error(c.rojo + 'La app no responde en ' + BASE + '. Arráncala antes de ejecutar la carga.' + c.reset + '\n');
    process.exit(1);
  }

  console.log(c.cyan + 'Generando tráfico concurrente...' + c.reset);
  const inicio = performance.now();

  const usuarios = Array.from({ length: CONCURRENCIA }, () => usuarioVirtual());
  await new Promise((res) => setTimeout(res, DURACION_S * 1000));
  corriendo = false;
  await Promise.all(usuarios);

  const segundos = (performance.now() - inicio) / 1000;
  const total = ok + errores;
  const throughput = total / segundos;
  const errorPct = total ? (errores / total) * 100 : 0;
  const p50 = percentil(latencias, 50);
  const p95 = percentil(latencias, 95);

  console.log('\n' + c.bold + '── RESULTADOS DE RENDIMIENTO ─────────────────────────' + c.reset);
  console.log('  Peticiones totales : ' + total);
  console.log('  Exitosas / Errores : ' + c.verde + ok + c.reset + ' / ' + (errores ? c.rojo : c.verde) + errores + c.reset);
  console.log('  Throughput         : ' + throughput.toFixed(1) + ' req/s');
  console.log('  Latencia p50       : ' + p50.toFixed(2) + ' ms');
  console.log('  Latencia p95       : ' + p95.toFixed(2) + ' ms');
  console.log('  Tasa de error      : ' + errorPct.toFixed(2) + ' %');

  const cumpleP95 = p95 < SLA_P95_MS;
  const cumpleError = errorPct < SLA_ERROR_PCT;
  const pasa = cumpleP95 && cumpleError;

  console.log('\n' + c.bold + '── EVALUACIÓN DEL QUALITY GATE (SLA) ─────────────────' + c.reset);
  console.log(
    '  p95 < ' +
      SLA_P95_MS +
      ' ms   : ' +
      (cumpleP95 ? c.verde + 'CUMPLE' : c.rojo + 'NO CUMPLE') +
      c.reset +
      ' (medido: ' +
      p95.toFixed(2) +
      ' ms)'
  );
  console.log(
    '  error < ' +
      SLA_ERROR_PCT +
      '%   : ' +
      (cumpleError ? c.verde + 'CUMPLE' : c.rojo + 'NO CUMPLE') +
      c.reset +
      ' (medido: ' +
      errorPct.toFixed(2) +
      '%)'
  );

  console.log('\n' + c.bold + '====================================================' + c.reset);
  if (pasa) {
    console.log('  ' + c.verde + c.bold + 'QUALITY GATE 2 (CARGA) EN VERDE — Cumple SLA (exit 0)' + c.reset);
  } else {
    console.log('  ' + c.rojo + c.bold + 'QUALITY GATE 2 (CARGA) EN ROJO — Viola SLA (exit 1)' + c.reset);
    console.log('  ' + c.gris + 'El pipeline detiene el despliegue automáticamente.' + c.reset);
  }
  console.log(c.bold + '====================================================' + c.reset + '\n');

  process.exit(pasa ? 0 : 1);
}

main();
