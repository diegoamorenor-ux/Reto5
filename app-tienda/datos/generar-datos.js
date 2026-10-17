/**
 * FASE 1 — Generación de Datos de Prueba Realistas con Faker y Semilla Fija
 *
 * Características:
 *   1. Usa @faker-js/faker con semilla fija (faker.seed(12345)) para garantizar
 *      datos 100% deterministas y reproducibles en cualquier máquina o agente CI/CD.
 *   2. Define 4 categorías cerradas ('hogar', 'tecnologia', 'ropa', 'juguetes')
 *      y genera 24 productos (20+) con campos coherentes (id, nombre, categoria,
 *      precio, descripcion, stock).
 *   3. Reto Extra: Si existe un dump ficticio (o lo genera y anonimiza al vuelo),
 *      incorpora la lista de clientes anonimizados (correos y nombres protegidos)
 *      en db.json sin exponer PII real.
 *
 * ¿Por qué NO se deben versionar los datos generados en un flujo CI/CD real?
 *   - Porque db.json es un artefacto derivado del código (generar-datos.js) y su semilla.
 *   - Versionar datos dinámicos genera conflictos de merge innecesarios cuando las
 *     pruebas mutan el estado (ej. al crear pedidos), ensucia el historial de Git y
 *     acopla las pruebas a un archivo estático en lugar de regenerar un entorno limpio
 *     y determinista en cada ejecución del pipeline (etapa Build / postinstall).
 */
import { faker } from '@faker-js/faker';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// 1. Semilla fija: garantiza exactamente el mismo catálogo en local, Docker y Azure Pipelines
const SEMILLA = 12345;
faker.seed(SEMILLA);

// 2. Al menos 4 categorías y 20+ productos (24 productos, 6 por categoría)
const CATEGORIAS = ['hogar', 'tecnologia', 'ropa', 'juguetes'];
const TOTAL_PRODUCTOS = 24;

const productos = Array.from({ length: TOTAL_PRODUCTOS }, (_, i) => {
  const categoria = CATEGORIAS[i % CATEGORIAS.length];
  return {
    id: i + 1,
    nombre: faker.commerce.productName(),
    categoria,
    precio: Number(faker.commerce.price({ min: 5, max: 500 })),
    descripcion: faker.commerce.productDescription(),
    stock: faker.number.int({ min: 1, max: 50 }),
  };
});

// 3. Cargar clientes anonimizados si existen (Reto Extra)
let clientesAnonimos = [];
const rutaAnonimos = path.join(__dirname, 'clientes-anonimos.json');
if (fs.existsSync(rutaAnonimos)) {
  try {
    clientesAnonimos = JSON.parse(fs.readFileSync(rutaAnonimos, 'utf-8'));
  } catch {
    clientesAnonimos = [];
  }
}

const db = {
  meta: {
    semilla: SEMILLA,
    totalProductos: productos.length,
    categorias: CATEGORIAS,
    clientesAnonimizados: clientesAnonimos.length,
  },
  productos,
  pedidos: [],
  clientes: clientesAnonimos,
};

// Escribir en el directorio actual (datos/db.json)
fs.mkdirSync(__dirname, { recursive: true });
const rutaDbLocal = path.join(__dirname, 'db.json');
fs.writeFileSync(rutaDbLocal, JSON.stringify(db, null, 2), 'utf-8');

// Si existe ../app-tienda/datos (cuando se ejecuta desde ./datos), sincronizar también allí
const rutaAppTiendaDatos = path.resolve(__dirname, '..', 'app-tienda', 'datos');
if (fs.existsSync(path.resolve(__dirname, '..', 'app-tienda'))) {
  fs.mkdirSync(rutaAppTiendaDatos, { recursive: true });
  fs.writeFileSync(path.join(rutaAppTiendaDatos, 'db.json'), JSON.stringify(db, null, 2), 'utf-8');
}

console.log(`datos/db.json generado con ${productos.length} productos en ${CATEGORIAS.length} categorías (semilla fija: ${SEMILLA}).`);
if (clientesAnonimos.length > 0) {
  console.log(`Incluidos ${clientesAnonimos.length} clientes anonimizados (Reto Extra GDPR).`);
}
