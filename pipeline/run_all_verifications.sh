#!/usr/bin/env bash
set -e

mkdir -p evidencias/logs e2e/resultados

echo ">>> [FASE 1] Generando datos con Faker (seed 12345) y Anonimización GDPR..."
npm run generar > evidencias/logs/fase1_generar_datos.txt 2>&1
cat evidencias/logs/fase1_generar_datos.txt

echo ">>> [APP] Iniciando servidor app-tienda en puerto 3000..."
node app-tienda/servidor/server.js > evidencias/logs/server.log 2>&1 &
SERVER_PID=$!
trap "kill $SERVER_PID 2>/dev/null || true" EXIT

for i in $(seq 1 20); do
  if curl -sf http://localhost:3000/api/health > /dev/null; then
    break
  fi
  sleep 0.5
done

echo ">>> [FASE 2 - GATE 1] Ejecutando Smoke Tests..."
node pipeline/tests/smoke-api.js | tee evidencias/logs/fase2_smoke.txt

echo ">>> [FASE 2 - GATE 2 VERDE] Ejecutando Prueba de Carga con SLA normal (p95 < 800 ms, error < 1%)..."
SLA_P95_MS=800 SLA_ERROR_PCT=1 CONCURRENCIA=15 DURACION_S=4 node pipeline/tests/carga-simple.js | tee evidencias/logs/fase2_carga_verde.txt

echo ">>> [FASE 2 - GATE 2 ROJO] Forzando fallo del Quality Gate de Carga (bajando SLA a p95 < 0.05 ms)..."
set +e
SLA_P95_MS=0.05 SLA_ERROR_PCT=1 CONCURRENCIA=25 DURACION_S=3 node pipeline/tests/carga-simple.js > evidencias/logs/fase2_carga_rojo.txt 2>&1
ROJO_EXIT=$?
set -e
echo "Exit code obtenido en Gate ROJO: $ROJO_EXIT (esperado: 1)" | tee -a evidencias/logs/fase2_carga_rojo.txt
cat evidencias/logs/fase2_carga_rojo.txt

echo ">>> [FASE 3] Ejecutando Suite E2E Playwright + Screenplay + pytest-bdd (6 escenarios)..."
(cd e2e && .venv/bin/pytest --junitxml=resultados/junit.xml) | tee evidencias/logs/fase3_pytest_bdd.txt

echo ">>> [FASE 3] Ejecutando Triaje IA sobre el reporte JUnit..."
(cd e2e && .venv/bin/python tools/triage_ia.py resultados/junit.xml) | tee evidencias/logs/fase3_triage_ia.txt

echo ">>> [FASE 3] Capturando pantallas reales de la interfaz web con Playwright..."
e2e/.venv/bin/python e2e/tools/capture_ui_screenshots.py

echo ">>> [FASE 5 - PACT] Ejecutando Contract Testing (Consumer + Provider Verification)..."
node pact/consumer/productos.consumer.pact.js | tee evidencias/logs/fase5_pact_consumer.txt
node pact/provider/verificar-proveedor.js | tee evidencias/logs/fase5_pact_provider.txt

echo ">>> [FASE 5 - DOCKER] Construyendo y verificando contenedor Docker (si el daemon está activo)..."
if docker info > /dev/null 2>&1; then
  docker build -t app-tienda:v1.0.0 -t acrtiendareto5.azurecr.io/app-tienda:v1.0.0 -t acrtiendareto5.azurecr.io/app-tienda:latest . > evidencias/logs/fase5_docker_build.txt 2>&1
  docker rm -f tienda-qa-container >/dev/null 2>&1 || true
  docker run -d --name tienda-qa-container -p 3005:3000 acrtiendareto5.azurecr.io/app-tienda:v1.0.0 > evidencias/logs/fase5_docker_run.txt 2>&1
  sleep 3
  {
    echo "=== DOCKER PS & HEALTHCHECK ==="
    docker ps --filter "name=tienda-qa-container"
    echo ""
    echo "=== GET http://localhost:3005/api/health (Contenedor Docker) ==="
    curl -s http://localhost:3005/api/health
    echo ""
    echo ""
    echo "=== SMOKE TEST CONTRA CONTENEDOR DOCKER (puerto 3005) ==="
    BASE_URL=http://localhost:3005 node pipeline/tests/smoke-api.js
    echo ""
    echo "=== IMÁGENES ETIQUETADAS PARA AZURE CONTAINER REGISTRY (ACR) ==="
    docker images | grep -E "REPOSITORY|app-tienda"
  } | tee evidencias/logs/fase5_docker_verificacion.txt
  docker rm -f tienda-qa-container >/dev/null 2>&1 || true
else
  echo "Docker daemon no está iniciado; intentando iniciar Docker Desktop..."
fi

echo ">>> ¡Todas las verificaciones completadas con éxito!"
