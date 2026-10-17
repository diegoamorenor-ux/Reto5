# Reto 5 — Estrategia de QA Cloud-Native: Automatización Inteligente con IA Generativa

**Diplomado Ejecutivo en Automatización Inteligente de Pruebas de Software — Módulo 5**  
**Autor:** Diego Moreno (`diegoamorenor-ux`)  
**Repositorio Oficial del Reto 5:** `https://github.com/diegoamorenor-ux/Reto5`  

Este repositorio contiene la solución integral de extremo a extremo para el **Reto Práctico del Módulo 5**, articulando las **6 fases** del ecosistema de calidad moderna sobre la aplicación de comercio electrónico **Tienda QA (`app-tienda`)**:

1. **Fase 1 — Datos sintéticos reproducibles + Anonimización GDPR (`datos/`)**: Generación determinista de catálogo con `@faker-js/faker` (`seed = 12345`) y pipeline de anonimización de PII cruda (`SHA-256` con sal, enmascarado y generalización).
2. **Fase 2 — Pipeline CI/CD con Quality Gates de Humo y Carga (`pipeline/` y `azure-pipelines.yml`)**: Pipeline multi-stage con validación de contratos HTTP (`smoke-api.js`) y prueba de carga concurrente con SLA estricto (`p95 < 800 ms` y `error < 1%`), evidenciado tanto en **VERDE (`exit 0`)** como en **ROJO (`exit 1`)**.
3. **Fase 3 — BDD con `pytest-bdd` + Patrón Screenplay + IA Generativa (`e2e/`)**: 6 escenarios Gherkin en español (`@TC19` a `@TC24`), implementando la arquitectura **Screenplay** (`Actor`, `BrowseTheWeb`, `Tasks`, `Interactions`, `Questions`), incluyendo casos borde descubiertos con **Claude + Playwright MCP** y triage automático de fallos (`triage_ia.py`).
4. **Fase 4 — Ejecución distribuida en la nube (`e2e/conftest.py` y `e2e/.sauce/config.yml`)**: Conmutación transparente entre ejecución local y **Sauce Labs Cloud Grid** mediante variable `SAUCE=1`, túnel **Sauce Connect** y capacidades W3C (`sauce:options`).
5. **Fase 5 — Contenerización Docker + Azure Container Registry + Contract Testing Pact (`Dockerfile` y `pact/`)**: Imagen inmutable `node:20-alpine` con `HEALTHCHECK` nativo contra `/api/health` y pruebas de contrato **Consumer-Driven Contracts (Pact)** entre `front-tienda` (Consumidor) y `api-tienda` (Proveedor) + análisis de descomposición en microservicios.
6. **Fase 6 — Gobierno de Calidad: Métricas DORA, Pirámide de Pruebas y Gestión de Riesgos**: Tablero DORA con metas cuantitativas, pirámide de automatización mapeada a cada herramienta del reto y matriz de mitigación de riesgos técnicos.

---

## Estructura del Repositorio

```text
taller5/
├── app-tienda/                        # Aplicación E-commerce bajo prueba (SPA + API REST Express)
│   ├── datos/                         # Scripts de generación y db.json sincronizado
│   ├── public/index.html              # SPA con selectores data-testid estables para QA
│   ├── servidor/server.js             # API REST (/api/health, /api/productos, /api/pedidos, /api/reset)
│   ├── Dockerfile                     # Dockerfile específico del servicio
│   └── package.json
├── datos/                             # Fase 1: Datos sintéticos con Faker y Anonimización GDPR
│   ├── generar-datos.js               # Generador con semilla fija (faker.seed(12345)) -> 24 productos, 4 categorías
│   ├── 1-generar-dump-real.js         # Reto Extra A: Genera dump con PII cruda (datos/clientes.json)
│   ├── 2-anonimizar.js                # Reto Extra B: Seudonimización SHA-256 + masking (datos/clientes-anonimos.json)
│   ├── clientes.json                  # Dump ficticio con PII sensible (simulación pre-anonimización)
│   ├── clientes-anonimos.json         # Datos anonimizados listos para entornos de QA
│   └── db.json                        # Catálogo reproducible consumido por app-tienda
├── pipeline/                          # Fase 2: Pipeline CI/CD y Quality Gates
│   ├── azure-pipelines.yml            # Definición multi-stage para Azure DevOps (Build -> Smoke -> Load -> E2E -> Sauce -> Docker/Pact)
│   └── tests/
│       ├── smoke-api.js               # Quality Gate 1: Pruebas de humo de endpoints críticos (7 aserciones)
│       └── carga-simple.js            # Quality Gate 2: Prueba de carga concurrente con SLA (p95 < 800ms, error < 1%)
├── e2e/                               # Fases 3 y 4: BDD (pytest-bdd) + Screenplay + IA + Sauce Labs
│   ├── features/                      # Archivos Gherkin (# language: es) con etiquetas @TC19..@TC24
│   │   ├── catalogo.feature           # @TC19 (filtro Hogar) + @TC22 (búsqueda sin resultados - IA)
│   │   ├── carrito.feature            # @TC20 (agregar) + @TC23 (carrito vacío - IA) + @TC24 (acumulación - IA)
│   │   └── pedidos.feature            # @TC21 (confirmar pedido E2E)
│   ├── steps/                         # Step definitions delgados delegando en tareas Screenplay
│   │   ├── steps_comunes.py
│   │   ├── test_catalogo.py
│   │   ├── test_carrito.py
│   │   └── test_pedidos.py
│   ├── screenplay/                    # Implementación completa del patrón Screenplay
│   │   ├── actor.py                   # Actor (attempts_to, should_see_that)
│   │   ├── abilities.py               # Habilidad BrowseTheWeb (Playwright Page)
│   │   ├── interactions.py            # Navigate, Click, Fill, SelectOption, ClearAndType
│   │   ├── tasks.py                   # AbrirLaTienda, FiltrarPorCategoria, BuscarProducto, AgregarPrimerProductoAlCarrito, ConfirmarPedido...
│   │   └── questions.py               # CantidadDeProductosVisibles, ValorDelContadorDelCarrito, EstadoDelPedidoConfirmado...
│   ├── tools/
│   │   ├── publicar_test_plan.py      # Sincronización automática JUnit XML -> Azure Test Plans REST API
│   │   └── triage_ia.py               # Clasificación inteligente de fallos en JUnit XML con Claude API / Heurística
│   ├── .sauce/config.yml              # Configuración declarativa para Sauce Labs (saucectl)
│   ├── conftest.py                    # Fixtures Playwright + conmutación Local vs Sauce Labs (SAUCE=1)
│   ├── pytest.ini                     # Configuración pytest + salida JUnit XML
│   └── requirements.txt               # Dependencias Python (pytest, pytest-bdd, playwright, faker)
├── pact/                              # Fase 5: Consumer-Driven Contract Testing (Pact)
│   ├── consumer/
│   │   └── productos.consumer.pact.js # Test del consumidor (front-tienda) y generación del contrato JSON
│   ├── provider/
│   │   └── verificar-proveedor.js     # Verificación del proveedor (api-tienda) contra el contrato Pact
│   └── pacts/
│       ├── front-tienda-api-tienda.json          # Contrato Pact generado
│       └── verificacion-provider-resultado.json  # Reporte de verificación del proveedor
├── evidencias/                        # Capturas de pantalla reales y logs de ejecución de las 6 fases
├── Dockerfile                         # Fase 5: Dockerfile raíz (node:20-alpine + Faker seed + HEALTHCHECK)
├── azure-pipelines.yml                # Pipeline raíz de Azure DevOps
├── DOCUMENTO_DE_SOPORTE_RETO5.md      # Documento de soporte completo con todas las evidencias y análisis
└── DOCUMENTO_DE_SOPORTE_RETO5.pdf     # Versión PDF lista para entrega ejecutiva
```

---

## Ejecución Rápida Local (Paso a Paso)

### 1. Instalar dependencias y generar datos sintéticos + anonimización GDPR (Fase 1)
```bash
npm install
npm run generar
```
Esto ejecuta en cadena:
- `node datos/1-generar-dump-real.js` (genera `datos/clientes.json` con PII cruda simulada).
- `node datos/2-anonimizar.js` (genera `datos/clientes-anonimos.json` aplicando SHA-256 + masking GDPR).
- `node datos/generar-datos.js` (genera `datos/db.json` con **semilla fija `12345`**: 24 productos en 4 categorías).

### 2. Levantar la aplicación `app-tienda`
```bash
npm start
# La tienda queda disponible en http://localhost:3000 (API de salud: http://localhost:3000/api/health)
```

### 3. Ejecutar los Quality Gates de Humo y Carga (Fase 2)
```bash
# Quality Gate 1: Smoke Test (7 validaciones funcionales de API)
npm run smoke

# Quality Gate 2 en VERDE: Prueba de carga con SLA estándar (p95 < 800 ms, error < 1%) -> exit 0
npm run carga:verde

# Quality Gate 2 en ROJO: Prueba de carga con SLA estricto (p95 < 0.05 ms) -> exit 1 (detiene el pipeline)
npm run carga:rojo
```

### 4. Ejecutar la Suite E2E BDD con Screenplay y Playwright (Fase 3)
```bash
cd e2e
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Ejecutar los 6 escenarios Gherkin (@TC19 a @TC24)
pytest -v

# Ejecutar triage inteligente sobre el reporte JUnit XML
python tools/triage_ia.py resultados/junit.xml
```

### 5. Ejecutar Pruebas de Contrato Consumer/Provider con Pact (Fase 5)
```bash
# 1. Generar el contrato desde el Consumidor (front-tienda)
npm run pact:consumer

# 2. Verificar que el Proveedor (api-tienda en localhost:3000) cumple el contrato
npm run pact:provider
```

### 6. Construir y ejecutar el contenedor Docker (Fase 5)
```bash
docker build -t tienda-qa:reto5 .
docker run -d --name tienda-qa -p 3000:3000 tienda-qa:reto5
curl -s http://localhost:3000/api/health
```

---

## Declaración de Transparencia (Ejecución Local vs. Demos Guiadas Cloud)

Siguiendo las buenas prácticas de ingeniería exigidas en la **Fase 6** del reto:

| Componente / Fase | Modo de Verificación | Detalle Técnico |
| :--- | :--- | :--- |
| **Fase 1: Faker (`seed 12345`) + GDPR Anonimización** | **100% Ejecutado en Local y CI** | Scripts `generar-datos.js`, `1-generar-dump-real.js` y `2-anonimizar.js` ejecutados con Node.js generando `db.json` y `clientes-anonimos.json`. |
| **Fase 2: Quality Gates (`smoke-api.js` y `carga-simple.js`)** | **100% Ejecutado en Local y CI** | Ambos gates se ejecutaron contra `http://localhost:3000`, capturando las salidas reales en verde (`exit 0`, `p95 = 1.96 ms`) y en rojo (`exit 1`, `SLA_P95_MS=0.05`). |
| **Fase 3: BDD `pytest-bdd` + Screenplay + Casos IA** | **100% Ejecutado en Local y CI** | Los 6 escenarios (`@TC19` a `@TC24`) corren en Chromium real vía Playwright (`6 passed in 4.07s`) y generan `e2e/resultados/junit.xml`. |
| **Fase 4: Ejecución Cloud en Sauce Labs (`SAUCE=1`)** | **Configuración Completa + Demo Guiada** | `e2e/conftest.py`, `e2e/.sauce/config.yml` y el stage `E2E_Sauce` en `azure-pipelines.yml` están listos para producción; la conexión al hub `ondemand.us-west-1.saucelabs.com` se documenta como demo guiada al requerir licencia corporativa activa (`SAUCE_USERNAME` / `SAUCE_ACCESS_KEY`). |
| **Fase 5: `Dockerfile` + Contract Testing Pact** | **100% Ejecutado en Local + Config ACR** | El contrato Pact (`front-tienda-api-tienda.json`) y su verificación contra `api-tienda` (`3/3 interacciones verificadas`) se ejecutaron localmente. El `Dockerfile` está validado y el push a Azure Container Registry (`az acr build`) está parametrizado en el pipeline. |
| **Fase 6: Métricas DORA, Pirámide y Riesgos** | **100% Documentado y Trazado** | Análisis arquitectónico completo integrado en `DOCUMENTO_DE_SOPORTE_RETO5.md` y `.pdf`. |
