/**
 * FASE 1 (Reto Extra - Parte B): Anonimización de datos sensibles (GDPR / Ley 1581).
 *
 * Toma datos/clientes.json (PII cruda simulada) y produce datos/clientes-anonimos.json
 * aplicando 4 técnicas de privacidad antes de integrarlos al catálogo de pruebas:
 *   1) Sustitución sintética determinista -> Nombre real reemplazado por alias de Faker (seed 777)
 *   2) Enmascaramiento (Masking)          -> Email y teléfono ocultan caracteres sensibles
 *   3) Hash criptográfico irreversible    -> Documento de identidad -> SHA-256 (12 hex chars)
 *   4) Generalización                     -> Fecha exacta de nacimiento -> solo el año
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { faker } from '@faker-js/faker';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rutaEntrada = path.join(__dirname, 'clientes.json');
const rutaSalida = path.join(__dirname, 'clientes-anonimos.json');

// Semilla fija para que la sustitución de nombres también sea reproducible
faker.seed(777);

export function maskEmail(email) {
  const [user, domain] = String(email).split('@');
  const tld = domain.split('.').pop();
  return `${user.slice(0, 2)}***@***.${tld}`;
}

export function maskTelefono(tel) {
  return String(tel).replace(/\d(?=\d{2})/g, '*');
}

export function hashDocumento(doc) {
  return crypto.createHash('sha256').update(String(doc)).digest('hex').slice(0, 12);
}

export function generalizarAnio(fechaISO) {
  return new Date(fechaISO).getFullYear();
}

export function ejecutarAnonimizacion() {
  if (!fs.existsSync(rutaEntrada)) {
    console.error('No existe datos/clientes.json. Ejecuta primero: node datos/1-generar-dump-real.js');
    process.exit(1);
  }

  const reales = JSON.parse(fs.readFileSync(rutaEntrada, 'utf-8'));

  const anonimos = reales.map((c) => ({
    id: c.id,
    nombre: faker.person.fullName(),                   // 1) Sustitución sintética
    email: maskEmail(c.email),                         // 2) Enmascarado de correo
    documento: hashDocumento(c.documento),             // 3) Hash SHA-256 irreversible
    telefono: maskTelefono(c.telefono),                // 2) Enmascarado de teléfono
    anio_nacimiento: generalizarAnio(c.fecha_nacimiento), // 4) Generalización a año
  }));

  fs.writeFileSync(rutaSalida, JSON.stringify(anonimos, null, 2), 'utf-8');

  const r = reales[0];
  const a = anonimos[0];
  console.log('===== FASE 1 (Reto Extra B): Anonimización GDPR Completada =====');
  console.log(`Anonimizados ${anonimos.length} registros en datos/clientes-anonimos.json\n`);
  console.log('ANTES  (PII cruda, NO apta para QA):');
  console.log(`  nombre="${r.nombre}"  email="${r.email}"`);
  console.log(`  documento="${r.documento}"  telefono="${r.telefono}"  nacimiento="${r.fecha_nacimiento}"\n`);
  console.log('DESPUÉS (Anonimizado, seguro para QA):');
  console.log(`  nombre="${a.nombre}"  email="${a.email}"`);
  console.log(`  documento="${a.documento}"  telefono="${a.telefono}"  anio_nacimiento=${a.anio_nacimiento}`);
  console.log('================================================================');

  return anonimos;
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url))) {
  ejecutarAnonimizacion();
}
