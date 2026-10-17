# Documento de Soporte — Reto 5: Estrategia de QA Cloud-Native y Automatización Inteligente con IA Generativa

- **Programa:** Diplomado Ejecutivo en Automatización Inteligente de Pruebas de Software — Módulo 5
- **Autor:** Diego Moreno (`diegoamorenor-ux`)
- **Repositorio de Referencia (Solo Lectura):** `https://github.com/oach82/Diplomado-Modulo5`
- **Aplicación Bajo Prueba (SUT):** E-commerce **Tienda QA (`app-tienda`)** — SPA + API REST (`Node.js / Express`)
- **Fecha:** Octubre 2026

---

## Tabla de Contenido

1. [Resumen Ejecutivo y Arquitectura de la Solución](#1-resumen-ejecutivo-y-arquitectura-de-la-solución)
2. [Fase 1 — Datos de Prueba Sintéticos con Faker y Anonimización GDPR (10 pts + Reto Extra)](#2-fase-1--datos-de-prueba-sintéticos-con-faker-y-anonimización-gdpr-10-pts--reto-extra)
3. [Fase 2 — Pipeline CI/CD con Quality Gates de Humo y Carga (15 pts)](#3-fase-2--pipeline-cicd-con-quality-gates-de-humo-y-carga-15-pts)
4. [Fase 3 — BDD con `pytest-bdd` + Patrón Screenplay + IA Generativa (20 pts + Reto Extra)](#4-fase-3--bdd-con-pytest-bdd--patrón-screenplay--ia-generativa-20-pts--reto-extra)
5. [Fase 4 — Ejecución Distribuida en la Nube con Sauce Labs y Azure Test Plans (10 pts)](#5-fase-4--ejecución-distribuida-en-la-nube-con-sauce-labs-y-azure-test-plans-10-pts)
6. [Fase 5 — Contenerización Docker, ACR y Pruebas de Contrato con Pact (15 pts + Reto Extra)](#6-fase-5--contenerización-docker-acr-y-pruebas-de-contrato-con-pact-15-pts--reto-extra)
7. [Fase 6 — Métricas DORA, Pirámide de Automatización y Gestión de Riesgos (20 pts)](#7-fase-6--métricas-dora-pirámide-de-automatización-y-gestión-de-riesgos-20-pts)
8. [Declaración de Transparencia: Ejecución Local vs. Demos Guiadas Cloud](#8-declaración-de-transparencia-ejecución-local-vs-demos-guiadas-cloud)

---

## 1. Resumen Ejecutivo y Arquitectura de la Solución

El presente documento presenta el diseño, implementación y evidencias de ejecución del **Reto 5**, cuyo objetivo es estructurar una estrategia de **Ingeniería de Calidad Cloud-Native** de punta a punta para la plataforma de comercio electrónico **Tienda QA (`app-tienda`)**.

La arquitectura implementada integra seis pilares fundamentales:
1. **Gobierno de Datos de Prueba (TDM & GDPR):** Generación determinista mediante `@faker-js/faker` con semilla fija (`12345`) y pipeline de seudonimización irreversible (`SHA-256` con sal + enmascarado) para proteger datos personales (PII).
2. **Continuous Testing & Quality Gates:** Pipeline declarativo (`azure-pipelines.yml`) donde cada etapa actúa como una compuerta de calidad bloqueante (*Fail-Fast*), validando salud de API (`smoke-api.js`) y acuerdos de nivel de servicio de rendimiento (`carga-simple.js`, exigiendo `p95 < 800 ms` y `error < 1%`).
3. **Automatización Basada en Comportamiento (BDD) + Patrón Screenplay + IA Generativa:** Suite E2E en Python (`pytest-bdd` + `Playwright`) desacoplada en **Actores, Habilidades (`BrowseTheWeb`), Tareas (`Tasks`), Interacciones (`Interactions`) y Preguntas (`Questions`)**, enriquecida con escenarios de borde generados mediante **Claude + Playwright MCP** y diagnóstico automatizado de fallos (`triage_ia.py`).
4. **Ejecución Distribuida en la Nube:** Capacidad de conmutar sin tocar el código de las pruebas entre ejecución local y **Sauce Labs Cloud Grid** (`SAUCE=1`) mediante túnel seguro **Sauce Connect** y sincronización de resultados JUnit hacia **Azure Test Plans**.
5. **Inmutabilidad con Docker y Contratos Consumer-Driven (Pact):** Empaquetado en imagen ligera `node:20-alpine` con `HEALTHCHECK` integrado, lista para **Azure Container Registry (ACR)**, acompañada de verificación formal de contratos API entre `front-tienda` (Consumidor) y `api-tienda` (Proveedor).
6. **Observabilidad y Gobierno DORA:** Mapeo completo de la Pirámide de Pruebas, cuadro de mando de métricas DORA y matriz de mitigación de riesgos operativos.

---

## 2. Fase 1 — Datos de Prueba Sintéticos con Faker y Anonimización GDPR (10 pts + Reto Extra)

### 2.1. Implementación del Generador Determinista (`datos/generar-datos.js`)
Para garantizar que las pruebas funcionales, de carga y de contrato sean **100% reproducibles** en cualquier máquina o agente de CI/CD, se implementó el generador `datos/generar-datos.js` fijando la semilla pseudoaleatoria `faker.seed(12345)`.

- **Categorías generadas (4):** `Hogar`, `Electrónica`, `Ropa`, `Deportes` (`6` productos por categoría = **24 productos** en total, cumpliendo el mínimo de $\ge 20$ productos en $\ge 3$ categorías).
- **Determinismo verificado:** Cada ejecución con la semilla `12345` produce exactamente los mismos nombres, precios, descripciones y stocks (por ejemplo, el producto `id: 1` siempre es `"Oriental Cotton Shoes"` en la categoría `"Hogar"` con precio `648.89` y stock `12`).

```javascript
// Extracto de datos/generar-datos.js
const { faker } = require('@faker-js/faker');

const SEED = Number(process.env.FAKER_SEED || 12345);
faker.seed(SEED);

const CATEGORIAS = ['Hogar', 'Electrónica', 'Ropa', 'Deportes'];
const PRODUCTOS_POR_CATEGORIA = 6; // 4 x 6 = 24 productos deterministas
```

### 2.2. ¿Por qué NO se versionan los datos generados en un pipeline real?
En un entorno industrial de CI/CD, los archivos volátiles o masivos generados sintéticamente (`db.json`, dumps de base de datos) **no deben versionarse en Git** por cuatro razones arquitectónicas:
1. **Reproducibilidad por código (*Data-as-Code*):** Al versionar el script `generar-datos.js` junto con la semilla (`FAKER_SEED=12345`) y la versión exacta de `@faker-js/faker` en `package-lock.json`, cualquier agente efímero del pipeline regenera exactamente el mismo dataset en menos de `200 ms` durante el stage de `Build`.
2. **Prevención de contaminación de estado (*State Drift*):** Durante la ejecución de pruebas (`POST /api/pedidos`), el archivo `db.json` sufre mutaciones de inventario y creación de pedidos. Si se versiona, genera conflictos constantes en Git (`merge conflicts`) y falsos positivos entre ramas.
3. **Seguridad y Cumplimiento Normativo (GDPR / Ley 1581):** Evitar el versionado de dumps en repositorios previene filtraciones accidentales de Información Personal Identificable (PII) en el historial inmutable de Git.
4. **Rendimiento del repositorio:** Mantener el repositorio liviano acelera el `git clone` en los agentes de Azure Pipelines y reduce el tamaño de las capas de construcción en Docker.

*(Nota: Para efectos de revisión académica de este reto, se incluye `datos/db.json` como evidencia directa del artefacto generado).*

### 2.3. Reto Extra Fase 1: Simulación de Dump con PII y Anonimización GDPR (`datos/1-generar-dump-real.js` y `datos/2-anonimizar.js`)
Se implementó el flujo completo de **Data Masking & Pseudonymization** exigido en el reto extra:
1. **`datos/1-generar-dump-real.js`:** Simula la extracción de producción generando `datos/clientes.json` con 15 clientes que contienen PII sensible expuesta (`nombre`, `email`, `documento`, `telefono`, `direccion`, `tarjeta_credito`, `fecha_nacimiento`).
2. **`datos/2-anonimizar.js`:** Aplica cuatro técnicas de privacidad de datos para producir `datos/clientes-anonimos.json`, apto para entornos de QA:
   - **Seudonimización determinista (`SHA-256` con sal):** El `documento` se transforma en un hash irreversible de 12 caracteres (`aea010c676aa`), preservando la integridad referencial sin exponer la cédula real.
   - **Sustitución sintética determinista:** El `nombre` y la `direccion` se reemplazan por valores de Faker sembrados con el propio hash del documento.
   - **Enmascarado parcial (*Masking*):** El correo (`monica1@gmail.com` $\rightarrow$ `mo***@***.com`), teléfono (`3961777575` $\rightarrow$ `********75`) y tarjeta (`****-****-****-8794`) ocultan la información sensible conservando el formato de validación.
   - **Generalización (*K-Anonymity*):** La fecha exacta de nacimiento (`1987-08-26`) se reduce únicamente al atributo `anio_nacimiento: 1987`, y el campo `fecha_nacimiento` original es eliminado.

### 2.4. Evidencia de Ejecución — Fase 1
![Evidencia Fase 1: Generación con Faker y Anonimización GDPR](evidencias/fase1_faker_anonimizacion.png)

---

## 3. Fase 2 — Pipeline CI/CD con Quality Gates de Humo y Carga (15 pts)

### 3.1. Diseño del Pipeline Multi-Stage (`pipeline/azure-pipelines.yml`)
Se diseñó el pipeline declarativo en `pipeline/azure-pipelines.yml` (y en la raíz `azure-pipelines.yml`) estructurado en etapas secuenciales donde cada stage depende del éxito del anterior (`dependsOn` + `condition: succeeded()`):

1. **`Stage 1: Build`** — Instala dependencias (`npm ci`), ejecuta la generación determinista de datos (`node datos/generar-datos.js`) con `FAKER_SEED=12345`, valida que el catálogo tenga $\ge 20$ productos y publica el artefacto `drop-app-tienda`.
2. **`Stage 2: SmokeTests` (Quality Gate 1)** — Levanta `app-tienda`, espera activamente a que `/api/health` responda HTTP 200 y ejecuta `pipeline/tests/smoke-api.js` (7 verificaciones de contrato funcional básico: salud, catálogo, filtro por categoría, búsqueda, detalle de producto, 404 controlado y creación de pedido). Si cualquier verificación falla, el script retorna `exit 1` y aborta el pipeline.
3. **`Stage 3: LoadTest` (Quality Gate 2 — Rendimiento)** — Ejecuta `pipeline/tests/carga-simple.js` generando tráfico concurrente contra `/api/productos` y evaluando la métrica percentil 95 (`p95`) y la tasa de error frente al SLA configurado:
   - **Umbral exigido:** `p95 < 800 ms` y `error < 1%`.
   - **Mecanismo de bloqueo:** Si `p95 >= SLA_P95_MS` o `errorRate >= SLA_ERROR_PCT`, el proceso invoca `process.exit(1)`, marcando el stage en **ROJO** en Azure DevOps e impidiendo el avance hacia pruebas E2E o despliegue en contenedores.

### 3.2. Evidencia del Quality Gate de Carga en VERDE (`SLA_P95_MS=800` $\rightarrow$ `exit 0`)
Con el umbral nominal de producción (`p95 < 800 ms` y `error < 1%`), la API procesó **59,748 peticiones** en 4 segundos con 15 usuarios virtuales concurrentes (`14,921.8 req/s`), registrando una latencia **`p50 = 0.85 ms`**, **`p95 = 1.96 ms`** y **`0.00%` de errores**, superando ampliamente el Quality Gate (`exit 0`).

![Evidencia Fase 2: Quality Gate de Carga en VERDE](evidencias/fase2_gate_carga_verde.png)

### 3.3. Evidencia del Quality Gate de Carga en ROJO (`SLA_P95_MS=0.05` $\rightarrow$ `exit 1`)
Para demostrar empíricamente que el Quality Gate detiene el pipeline ante una degradación de rendimiento, se redujo el umbral permitido a un valor imposible de cumplir (`SLA_P95_MS=0.05 ms` con 25 usuarios concurrentes). La latencia medida fue `p95 = 2.81 ms`, lo cual disparó la condición `NO CUMPLE`, emitiendo **`exit code 1`** y bloqueando inmediatamente las etapas subsiguientes.

![Evidencia Fase 2: Quality Gate de Carga en ROJO](evidencias/fase2_gate_carga_rojo.png)

---

## 4. Fase 3 — BDD con `pytest-bdd` + Patrón Screenplay + IA Generativa (20 pts + Reto Extra)

### 4.1. Arquitectura Screenplay Implementada (`e2e/screenplay/`)
A diferencia del patrón tradicional *Page Object Model (POM)* —que tiende a convertirse en clases monolíticas acopladas a selectores—, en este reto se implementó el **Patrón Screenplay** siguiendo el principio de Responsabilidad Única (SRP) y Open/Closed (OCP):

- **Actor (`e2e/screenplay/actor.py`):** Representa al usuario de negocio (`Cliente QA`). Ejecuta tareas mediante `actor.attempts_to(*tasks)` y valida el estado del sistema mediante `actor.should_see_that(question, matcher)`.
- **Abilities (`e2e/screenplay/abilities.py`):** La habilidad `BrowseTheWeb.using(page)` encapsula la instancia de `playwright.sync_api.Page`.
- **Interactions (`e2e/screenplay/interactions.py`):** Acciones atómicas de bajo nivel sobre la interfaz: `Navigate.to(url)`, `Click.on(selector)`, `Fill.field(selector, value)`, `SelectOption.by_value(selector, value)`, `ClearAndType.into(selector, text)`.
- **Tasks (`e2e/screenplay/tasks.py`):** Acciones de alto nivel con semántica de dominio compuestas por interacciones:
  - `AbrirLaTienda(base_url)`
  - `FiltrarPorCategoria(categoria)`
  - `BuscarProductoPorTexto(termino)`
  - `AgregarPrimerProductoAlCarrito()`
  - `AgregarPrimerProductoAlCarritoVariasVeces(veces)`
  - `AbrirDetalleDelCarrito()`
  - `ConfirmarPedidoDelCarrito()`
- **Questions (`e2e/screenplay/questions.py`):** Consultas observables sobre el estado actual del DOM:
  - `CantidadDeProductosVisibles()`
  - `CategoriasDeProductosVisibles()`
  - `MensajeSinResultadosVisible()`
  - `ValorDelContadorDelCarrito()`
  - `TextoDelCarritoVacio()`
  - `CantidadDelPrimerItemEnCarrito()`
  - `EstadoDelPedidoConfirmado()`

### 4.2. Casos Manuales Traducidos a Gherkin + Escenarios de Borde Generados con IA
Se implementaron **6 escenarios Gherkin en español** (`# language: es`) distribuidos en 3 archivos `.feature` (`catalogo.feature`, `carrito.feature`, `pedidos.feature`), superando el mínimo requerido de 4 escenarios e incluyendo el **Reto Extra** de casos borde generados con IA:

| ID / Tag | Archivo `.feature` | Escenario Gherkin | Origen | Resultado |
| :--- | :--- | :--- | :--- | :---: |
| **`@TC19`** | `catalogo.feature` | Filtrar productos por categoría `"Hogar"` muestra solo productos de esa categoría | Caso Manual 1 | `PASSED` |
| **`@TC20`** | `carrito.feature` | Agregar un producto al carrito incrementa el contador a `"1"` | Caso Manual 2 | `PASSED` |
| **`@TC21`** | `pedidos.feature` | Confirmar un pedido con un producto genera estado `"confirmado"` | Caso Manual 3 | `PASSED` |
| **`@TC22`** | `catalogo.feature` | Buscar un producto inexistente (`"xyzinexistente999"`) muestra mensaje de sin resultados | **IA Generativa + MCP (Borde 1)** | `PASSED` |
| **`@TC23`** | `carrito.feature` | Abrir el carrito sin productos muestra mensaje `"Tu carrito está vacío"` y oculta confirmar | **IA Generativa + MCP (Borde 2)** | `PASSED` |
| **`@TC24`** | `carrito.feature` | Agregar el mismo producto dos veces acumula la cantidad (`x2`) e incrementa el badge a `"2"` | **IA Generativa + MCP (Borde 3)** | `PASSED` |

### 4.3. Prompt Utilizado con Claude + Playwright MCP para Descubrir y Generar los Escenarios de Borde
Para generar los escenarios `@TC22`, `@TC23` y `@TC24` (y sus respectivas *Tasks* y *Questions* en Screenplay), se conectó el servidor **Playwright MCP** (`@playwright/mcp`) y se utilizó el siguiente **Prompt estructurado**:

```markdown
Actúa como un Arquitecto Senior de QA Automatizado especialista en BDD (pytest-bdd) y el patrón Screenplay.
Usa la herramienta Playwright MCP para navegar a http://localhost:3000 (Tienda QA), inspeccionar el árbol de accesibilidad y los atributos `data-testid` del DOM en vivo, y realizar lo siguiente:

1. Explora los comportamientos límite (edge cases) de la SPA en:
   - El buscador de texto (`[data-testid="input-buscar"]`) cuando no existen coincidencias.
   - El panel del carrito (`[data-testid="panel-carrito"]`) cuando se abre sin haber agregado productos.
   - La acumulación de unidades cuando un mismo producto se agrega múltiples veces seguidas.
2. Genera 3 escenarios Gherkin en español (`# language: es`) etiquetados con `@ia_generado`, `@borde` y `@TC22`, `@TC23`, `@TC24`, siguiendo exactamente el estilo declarativo de `catalogo.feature` y `carrito.feature`.
3. Genera las Tasks (`BuscarProductoPorTexto`, `AbrirDetalleDelCarrito`, `AgregarPrimerProductoAlCarritoVariasVeces`) y Questions (`MensajeSinResultadosVisible`, `TextoDelCarritoVacio`, `CantidadDelPrimerItemEnCarrito`) necesarias en `e2e/screenplay/` respetando el desacoplamiento del patrón Screenplay (sin usar selectores crudos dentro de `steps/`).
```

![Evidencia Fase 3: Exploración y Generación de Escenarios con Claude + Playwright MCP](evidencias/fase3_claude_mcp_generacion.png)

### 4.4. Evidencia de Ejecución de `pytest` en Verde y Triage con IA (`triage_ia.py`)
La ejecución completa de la suite (`pytest -v`) sobre Chromium real finalizó con **6 escenarios en VERDE (`6 passed in 4.07s`)**, generando el reporte estándar `e2e/resultados/junit.xml` y validando su análisis mediante `e2e/tools/triage_ia.py`.

![Evidencia Fase 3: Salida de pytest-bdd en VERDE y Triage IA](evidencias/fase3_pytest_bdd_verde.png)

### 4.5. Capturas Reales de la Interfaz Automatizada con Playwright (Casos Nominales y Casos Borde IA)

| Catálogo Completo (`app-tienda`) | Filtro por Categoría `"Hogar"` (`@TC19`) |
| :---: | :---: |
| ![Catálogo Completo](evidencias/ui_01_catalogo_completo.png) | ![Filtro Hogar](evidencias/ui_02_catalogo_filtrado_hogar.png) |

| Caso Borde IA `@TC22`: Búsqueda Sin Resultados | Caso Borde IA `@TC23`: Carrito Vacío |
| :---: | :---: |
| ![Búsqueda sin resultados](evidencias/ui_03_borde_ia_sin_resultados.png) | ![Carrito vacío](evidencias/ui_04_borde_ia_carrito_vacio.png) |

| Caso Borde IA `@TC24`: Carrito Acumulado (`x2`) | Flujo E2E `@TC21`: Pedido Confirmado |
| :---: | :---: |
| ![Carrito acumulado](evidencias/ui_05_carrito_acumulado_ia.png) | ![Pedido confirmado](evidencias/ui_06_pedido_confirmado.png) |

---

## 5. Fase 4 — Ejecución Distribuida en la Nube con Sauce Labs y Azure Test Plans (10 pts)

### 5.1. Configuración Dual Local / Cloud (`e2e/conftest.py` y `e2e/.sauce/config.yml`)
El archivo `e2e/conftest.py` implementa la detección dinámica del entorno mediante la variable `SAUCE=1`. Los archivos `.feature`, los `steps` y las clases del patrón `Screenplay` **no sufren ningún cambio** al pasar de ejecución local a la nube:

- **En Modo Local (`SAUCE=0` por defecto):**
  - Invoca `playwright.chromium.launch(headless=True)` directamente sobre el binario local de Chromium.
  - Conecta contra `http://localhost:3000`.
- **En Modo Cloud (`SAUCE=1` en el stage `E2E_Sauce` del pipeline):**
  - Construye el diccionario estándar **W3C WebDriver / CDP Capabilities (`sauce:options`)** inyectando credenciales desde las variables secretas `SAUCE_USERNAME` y `SAUCE_ACCESS_KEY`, el identificador del túnel `tunnelName` (`SAUCE_TUNNEL_NAME`), el `build` (`azure-build-$(Build.BuildNumber)`), el nombre del escenario y las etiquetas (`@TC19`..`@TC24`).
  - Conecta el navegador remoto en la nube de Sauce Labs (`ondemand.us-west-1.saucelabs.com`) hacia el servidor `app-tienda` que corre en el agente privado de CI a través del túnel seguro **Sauce Connect Proxy (`sc run`)**.
  - Al finalizar cada escenario (`pytest_runtest_makereport`), reporta automáticamente el estado `passed` o `failed` a Sauce Labs (`sauce:job-result=...`) para que quede grabado junto al video y los logs HAR.
- **Sincronización con Azure Test Plans (`e2e/tools/publicar_test_plan.py`):**
  - Lee `e2e/resultados/junit.xml`, extrae el marcador `@TC<id>` de cada prueba y consume la API REST de Azure DevOps (`/_apis/test/Runs`) para publicar el resultado directamente sobre los Test Cases `19, 20, 21, 22, 23, 24` del Test Plan corporativo.

### 5.2. Comparativa Técnica: ¿Qué cambia entre la ejecución Local y la Nube?

| Dimensión | Ejecución Local (`SAUCE=0`) | Ejecución en la Nube (`SAUCE=1` — Sauce Labs) |
| :--- | :--- | :--- |
| **Infraestructura del Navegador** | Proceso Chromium local en la máquina del desarrollador o runner efímero. | Granjas de VMs/Contenedores aislados en **Sauce Labs Cloud Grid** (múltiples OS y versiones de navegador en paralelo). |
| **Acceso a `localhost:3000`** | Loopback directo (`127.0.0.1:3000`). | Requiere túnel cifrado **Sauce Connect (`sc`)** para exponer de forma segura el puerto `3000` del agente CI hacia la nube de Sauce Labs. |
| **Observabilidad y Evidencia** | Reporte JUnit XML local y capturas manuales. | **Video completo de la sesión**, trazas de red **HAR**, logs de consola DOM, metadatos de build y estado sincronizado en **Azure Test Plans**. |
| **Código de Pruebas (`.feature` / `Screenplay`)** | **Idéntico (0 líneas modificadas).** | **Idéntico (0 líneas modificadas)**; toda la abstracción reside en el fixture `browser_page` de `e2e/conftest.py` y `.sauce/config.yml`. |

### 5.3. Evidencia de Configuración y Demo Guiada — Sauce Labs & Azure Test Plans
![Evidencia Fase 4: Ejecución Cloud en Sauce Labs y Sincronización con Azure Test Plans](evidencias/fase4_sauce_labs_cloud.png)

---

## 6. Fase 5 — Contenerización Docker, ACR y Pruebas de Contrato con Pact (15 pts + Reto Extra)

### 6.1. Empaquetado Inmutable en `Dockerfile` y Registro en Azure Container Registry (ACR)
Se creó el `Dockerfile` en la raíz del proyecto (y en `app-tienda/Dockerfile`) utilizando una imagen base oficial ligera (`node:20-alpine`), instalando únicamente dependencias de producción (`npm ci --omit=dev`), pre-generando el catálogo determinista con `FAKER_SEED=12345` durante la construcción de la imagen y configurando un `HEALTHCHECK` nativo cada 15 segundos contra `http://localhost:3000/api/health`:

```dockerfile
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV FAKER_SEED=12345

COPY app-tienda/package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY app-tienda/servidor ./servidor
COPY app-tienda/public ./public
COPY datos ./datos

RUN node datos/generar-datos.js
EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "servidor/server.js"]
```

En el stage `Docker_Pact` de `azure-pipelines.yml`, la imagen se construye, se verifica su estado `healthy` y se publica en **Azure Container Registry (`acr.azurecr.io/tienda-qa:$(Build.BuildId)`)**.

![Evidencia Fase 5: Contenedor Docker saludable y registro en ACR](evidencias/fase5_docker_acr.png)

### 6.2. Pruebas de Contrato Consumer-Driven con Pact (`pact/`)
Para evitar romper la integración entre el frontend (`front-tienda`) y el backend (`api-tienda`) sin depender de costosas pruebas E2E para detectar cambios de esquema JSON, se implementó el flujo **Consumer-Driven Contract Testing**:

1. **Fase Consumidor (`pact/consumer/productos.consumer.pact.js`):**
   - Define las expectativas exactas del consumidor `front-tienda` sobre 3 interacciones clave:
     - `GET /api/productos` $\rightarrow$ HTTP `200`, `Content-Type: application/json`, arreglo con al menos 20 productos con tipos estrictos (`id: integer`, `nombre: string`, `categoria: string`, `precio: number`, `stock: integer`).
     - `GET /api/productos/1` $\rightarrow$ HTTP `200`, objeto de detalle del producto `id = 1`.
     - `POST /api/pedidos` $\rightarrow$ enviando `{ cliente: "Ana Cliente QA", items: [{ id: 1, cantidad: 2 }] }`, espera HTTP `201` con `{ id: integer, estado: "confirmado", total: number }`.
   - Genera el artefacto formal de contrato en **`pact/pacts/front-tienda-api-tienda.json`**.
2. **Fase Proveedor (`pact/provider/verificar-proveedor.js`):**
   - Lee el contrato `pact/pacts/front-tienda-api-tienda.json` y reproduce cada solicitud HTTP contra el proveedor real `api-tienda` (`http://localhost:3000`), validando códigos de estado, cabeceras y reglas de coincidencia de tipos (`matchers`).
   - Resultado obtenido: **3 de 3 interacciones verificadas con éxito (`0 fallidas`)**, generando el reporte `pact/pacts/verificacion-provider-resultado.json`.

![Evidencia Fase 5: Verificación de Contrato Pact Consumer y Provider en VERDE](evidencias/fase5_pact_contract.png)

### 6.3. Reto Extra Fase 5: De Monolito a Microservicios — Arquitectura de Contratos Pact
Actualmente `app-tienda` opera como un monolito modular que sirve tanto el frontend como los endpoints `/api/productos` y `/api/pedidos`. Al evolucionar hacia una **arquitectura de microservicios**, el sistema se descompone en cuatro servicios independientes y los contratos Pact se multiplican así:

| Microservicio / Componente | Rol en Contratos Pact | Contratos Pact Requeridos (`Consumer -> Provider`) | ¿Qué previene cada contrato? |
| :--- | :--- | :--- | :--- |
| **`front-tienda` (SPA / BFF)** | **Consumer** | 1. `front-tienda -> ms-catalogo` (`GET /api/productos`)<br>2. `front-tienda -> ms-pedidos` (`POST /api/pedidos`) | Previene que un cambio de nombre de atributo (ej. `precio` $\rightarrow$ `unitPrice`) en catálogo o pedidos rompa el renderizado de la SPA. |
| **`ms-pedidos` (Orquestador de Órdenes)** | **Provider** (frente al Front) y **Consumer** (frente a Catálogo y Pagos) | 3. `ms-pedidos -> ms-catalogo` (`PATCH /api/inventario/reservar`)<br>4. `ms-pedidos -> ms-pagos` (`POST /api/cobros`) | Garantiza que al confirmar un pedido, `ms-pedidos` pueda descontar stock en `ms-catalogo` y procesar el pago sin errores de serialización. |
| **`ms-catalogo` (Inventario y Productos)** | **Provider** | Verifica los contratos publicados en el **Pact Broker** tanto por `front-tienda` como por `ms-pedidos`. | Impide desplegar una versión de `ms-catalogo` si rompe cualquiera de sus dos consumidores (`can-i-deploy`). |
| **`ms-notificaciones` (Eventos Asíncronos)** | **Consumer (Message Pact)** | 5. `ms-notificaciones -> ms-pedidos` (Evento `PedidoConfirmadoEvent` en Kafka/Service Bus) | Valida contratos de mensajería asíncrona sin necesidad de levantar un broker Kafka real durante el unit test. |

---

## 7. Fase 6 — Métricas DORA, Pirámide de Automatización y Gestión de Riesgos (20 pts)

### 7.1. Cuadro de Mando de Métricas DORA (DevOps Research and Assessment)
A continuación, se presenta cómo la arquitectura implementada en las Fases 1 a 5 impacta y mide los **4 indicadores clave de rendimiento DORA**:

| Métrica DORA | Definición Operativa | Meta en el Proyecto (Nivel Elite/High) | Cómo se mide y habilita en nuestro Pipeline (`taller5`) |
| :--- | :--- | :--- | :--- |
| **1. Deployment Frequency (DF)** *(Frecuencia de Despliegue)* | Con qué frecuencia la organización despliega código exitosamente a producción. | **Múltiples despliegues bajo demanda por día** (cada merge a `main` que supere los Quality Gates). | Medido por el número de ejecuciones exitosas del stage `Docker_Pact` que publican una nueva imagen `tienda-qa:$(Build.BuildId)` en ACR. La automatización del 100% de las pruebas elimina cuellos de botella manuales. |
| **2. Lead Time for Changes (LT)** *(Tiempo de Entrega de Cambios)* | Tiempo transcurrido desde que se hace `git commit` hasta que el cambio está validado y listo para producción. | **$< 15\text{ minutos}$** (Ejecución local completa en $\approx 12\text{ segundos}$; pipeline completo en nube $< 8\text{ minutos}$). | Los Quality Gates rápidos (*Fail-Fast*: Smoke en `1s`, Carga en `4s`, Pact en `1s`, E2E BDD en `4s`) brindan retroalimentación inmediata antes de construir o desplegar contenedores pesados. |
| **3. Change Failure Rate (CFR)** *(Tasa de Fallo por Cambio)* | Porcentaje de despliegues que causan una degradación o incidente en producción. | **$< 5\%$** | Reducido drásticamente mediante **3 barreras preventivas**: (1) Pact Contract Testing evita rupturas de API, (2) Load Quality Gate (`p95 < 800ms`) bloquea regresiones de latencia, y (3) 6 escenarios BDD cubren flujos nominales y bordes. |
| **4. Mean Time to Restore (MTTR)** *(Tiempo Medio de Recuperación)* | Tiempo requerido para diagnosticar y restaurar el servicio tras un fallo en el pipeline o en producción. | **$< 10\text{ minutos}$** | Acelerado por dos mecanismos: (1) **`e2e/tools/triage_ia.py`** que analiza instantáneamente `junit.xml` con IA clasificando la causa raíz (*UI/API/Timing*), y (2) imágenes inmutables en **ACR** que permiten *rollback* inmediato al tag anterior, sumado al `HEALTHCHECK` automático de Docker. |

### 7.2. Pirámide de Automatización de Pruebas del Proyecto
La estrategia implementada respeta estrictamente las proporciones saludables de la **Pirámide de Cohn**, concentrando la velocidad y el volumen en la base y reservando la cima para flujos críticos de negocio:

```mermaid
flowchart TD
    subgraph CIMA ["CIMA: Pruebas E2E UI & Cloud Cross-Browser (15% - Lento / Alto Costo)"]
        E2E["Fase 3 y 4: pytest-bdd + Patrón Screenplay + Playwright + Sauce Labs\n6 Escenarios Gherkin (@TC19..@TC24) | 4.07 s local | Video + HAR en Cloud"]
    end

    subgraph CENTRO ["CAPA MEDIA: Contratos API, Humo y Rendimiento (35% - Velocidad Media)"]
        PACT["Fase 5: Contract Testing con Pact (Consumer front-tienda / Provider api-tienda)\n3 Interacciones verificadas en < 1 s (Sin navegador)"]
        SMOKE["Fase 2: Quality Gate 1 — Smoke API (pipeline/tests/smoke-api.js)\n7 Aserciones HTTP críticas en < 1 s"]
        LOAD["Fase 2: Quality Gate 2 — Carga & SLA (pipeline/tests/carga-simple.js)\n~60,000 req en 4 s | SLA: p95 < 800 ms y error < 1%"]
    end

    subgraph BASE ["BASE: Datos Sintéticos Deterministas & Anonimización Segura (50% - Ultra Rápido)"]
        FAKER["Fase 1: Datos Deterministas (@faker-js/faker seed=12345)\n24 productos en 4 categorías + Seudonimización GDPR SHA-256 (< 0.2 s)"]
    end

    FAKER --> PACT
    FAKER --> SMOKE
    SMOKE --> LOAD
    PACT --> E2E
    LOAD --> E2E
```

![Evidencia Fase 6: Pirámide de Pruebas, Métricas DORA y Matriz de Riesgos](evidencias/fase6_piramide_dora.png)

### 7.3. Matriz de Riesgos de Calidad y Estrategias de Mitigación (3 Riesgos Críticos)

| # | Riesgo Identificado | Impacto en el Negocio / Pipeline | Probabilidad | Estrategia de Mitigación Implementada en el Reto 5 |
| :-: | :--- | :--- | :---: | :--- |
| **R1** | **Inestabilidad y *Flakiness* en Pruebas E2E por Datos Mutables o Selectores Frágiles** | Falsos negativos que detienen despliegues legítimos y erosionan la confianza del equipo en el pipeline CI/CD. | Alta | 1. Fijación de semilla determinista `faker.seed(12345)` en `generar-datos.js`.<br>2. Invocación de `POST /api/reset` en el fixture `reset_tienda_state` (`e2e/conftest.py`) antes de cada escenario.<br>3. Uso exclusivo de atributos inmutables `data-testid` encapsulados en el patrón **Screenplay**. |
| **R2** | **Degradación Silenciosa de Rendimiento bajo Concurrencia o Ruptura de Contratos API** | Caída del checkout en horas pico o pantallas en blanco en el frontend tras un cambio en el backend que pasa las pruebas unitarias. | Media | 1. **Quality Gate Bloqueante de Carga (`carga-simple.js`):** Aborta el pipeline con `exit 1` si `p95 >= 800 ms` o `error >= 1%`.<br>2. **Consumer-Driven Contracts (`pact/`):** Verifica que cualquier cambio en `api-tienda` respete el contrato JSON esperado por `front-tienda` antes de desplegar. |
| **R3** | **Exposición de Datos Personales Reales (PII) en Entornos de QA o Nubes Externas (Sauce Labs)** | Sanciones legales severas por incumplimiento de GDPR / Ley de Protección de Datos al enviar nombres, cédulas o correos reales a logs de terceros. | Media | 1. Prohibición de dumps crudos en QA mediante el pipeline de anonimización **`datos/2-anonimizar.js`** (hashing `SHA-256` con sal para documentos, enmascarado de emails/teléfonos y generalización de fecha de nacimiento).<br>2. Generación 100% sintética en contenedores Docker. |

---

## 8. Declaración de Transparencia: Ejecución Local vs. Demos Guiadas Cloud

En cumplimiento del criterio de evaluación de honestidad técnica de la **Fase 6**, se detalla con total precisión qué componentes fueron ejecutados en vivo sobre el entorno local de trabajo y cuáles corresponden a configuraciones listas para producción acompañadas de evidencia de demo guiada:

1. **Ejecutado 100% en Vivo en Entorno Local (con logs y capturas reales en `evidencias/`):**
   - **Fase 1:** Ejecución real de `datos/1-generar-dump-real.js`, `datos/2-anonimizar.js` y `datos/generar-datos.js` (`seed = 12345`), produciendo `datos/clientes.json`, `datos/clientes-anonimos.json` y `datos/db.json` (24 productos en 4 categorías).
   - **Fase 2:** Ejecución real del servidor `app-tienda` (`http://localhost:3000`), prueba de humo `pipeline/tests/smoke-api.js` (`7/7 OK`), prueba de carga `pipeline/tests/carga-simple.js` en **VERDE** (`p95 = 1.96 ms < 800 ms`, `exit 0`) y prueba de carga en **ROJO** modificando el SLA (`SLA_P95_MS=0.05`, `p95 = 2.81 ms`, `exit 1`).
   - **Fase 3:** Ejecución real con `pytest` (`pytest-bdd 9.0.0` + `Playwright 1.58.0` sobre Chromium headless) de los **6 escenarios Gherkin** (`@TC19` a `@TC24`, incluyendo los 3 escenarios borde generados con IA) implementados con el patrón **Screenplay**, obteniendo `6 passed in 4.07s`, reporte `e2e/resultados/junit.xml`, capturas reales de la UI (`evidencias/ui_01_*.png` a `ui_06_*.png`) y ejecución real de `e2e/tools/triage_ia.py`.
   - **Fase 5 (Pact Contract Testing):** Ejecución real del test de consumidor (`pact/consumer/productos.consumer.pact.js`) generando `pact/pacts/front-tienda-api-tienda.json` y verificación real contra el proveedor en vivo (`pact/provider/verificar-proveedor.js`), logrando `3/3 interacciones verificadas`.
2. **Configurado Integralmente en Código + Evidenciado como Demo Guiada (Servicios Cloud con Credenciales Externas):**
   - **Fase 4 (Sauce Labs Cloud Grid + Sauce Connect + Azure Test Plans):** El soporte completo en código (`e2e/conftest.py` con `SAUCE=1`, `e2e/.sauce/config.yml`, `e2e/tools/publicar_test_plan.py` y el stage `E2E_Sauce` en `azure-pipelines.yml`) está implementado. Dado que la conexión remota a `ondemand.us-west-1.saucelabs.com` y Azure DevOps requiere suscripciones empresariales (`SAUCE_ACCESS_KEY`, `AZDO_PAT`), su ejecución en nube se presenta como demo guiada arquitectónica.
   - **Fase 5 (Docker Runtime & Push a Azure Container Registry `acr.azurecr.io`):** El `Dockerfile` multi-etapa con `HEALTHCHECK` y el stage `Docker_Pact` están completamente construidos y validados sintácticamente; el push hacia `acr.azurecr.io/tienda-qa` se documenta como demo guiada al requerir una suscripción activa de Azure.
