/**
 * FASE 1 (Reto Extra - Parte A): Generar un "dump real" ficticio de clientes.
 *
 * Simula una extracción de producción con Información Personal Identificable (PII):
 * nombre completo, correo electrónico personal, documento de identidad, teléfono
 * y fecha exacta de nacimiento.
 *
 * IMPORTANTE: En un entorno real, este dump NUNCA debe usarse directamente en QA
 * ni subirse al repositorio sin pasar antes por el proceso de anonimización (GDPR / Ley 1581).
 */
import { faker } from '@faker-js/faker';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rutaDump = path.join(__dirname, 'clientes.json');

const CANTIDAD_CLIENTES = 15;

// Semilla fija para simular el dump de producción de forma determinista
faker.seed(2024);

function documentoAleatorio() {
  return String(faker.number.int({ min: 1000000000, max: 9999999999 }));
}

function telefonoAleatorio() {
  return String(faker.number.int({ min: 3000000000, max: 3999999999 }));
}

function crearClienteReal(id) {
  return {
    id,
    nombre: faker.person.fullName(),
    email: faker.internet.email().toLowerCase(),
    documento: documentoAleatorio(),
    telefono: telefonoAleatorio(),
    fecha_nacimiento: faker.date
      .birthdate({ min: 18, max: 80, mode: 'age' })
      .toISOString()
      .slice(0, 10),
  };
}

const clientesReales = Array.from({ length: CANTIDAD_CLIENTES }, (_, i) =>
  crearClienteReal(i + 1)
);

fs.mkdirSync(__dirname, { recursive: true });
fs.writeFileSync(rutaDump, JSON.stringify(clientesReales, null, 2), 'utf-8');

console.log('===== FASE 1 (Reto Extra A): Dump "real" ficticio generado =====');
console.log(`Generados ${clientesReales.length} clientes con PII en datos/clientes.json`);
console.log(
  `Ejemplo PII (CRUDO): ${clientesReales[0].nombre} | ${clientesReales[0].email} | doc: ${clientesReales[0].documento} | tel: ${clientesReales[0].telefono}`
);
console.log('Siguiente paso: node datos/2-anonimizar.js');
console.log('================================================================');
