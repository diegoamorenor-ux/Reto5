"""Configuración compartida de pytest para las pruebas E2E (Fases 3 y 4).

Las MISMAS pruebas (Playwright + Screenplay + pytest-bdd) pueden ejecutarse en
LOCAL o en la NUBE (Sauce Labs) cambiando únicamente variables de entorno /
capabilities, sin tocar ni una sola línea de los features ni del código Screenplay.

Ejecución local (por defecto):
    pytest

Ejecución en Sauce Labs (Fase 4 - Nube):
    SAUCE=1
    SAUCE_USERNAME=<tu-usuario>
    SAUCE_ACCESS_KEY=<tu-access-key>
    SAUCE_REGION=us-west-1            # us-west-1 | eu-central-1
    SAUCE_BROWSER=chrome              # chrome | MicrosoftEdge | firefox
    SAUCE_PLATFORM="Windows 11"       # Sistema operativo del navegador real en la nube
    SAUCE_TUNNEL=<nombre-tunel>       # Opcional: túnel Sauce Connect hacia localhost
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent))

from screenplay.actor import Actor
from screenplay.abilities import NavegarConElNavegador


def _usar_sauce() -> bool:
    """Devuelve True si se solicitó correr en Sauce Labs (SAUCE=1) y hay credenciales."""
    return os.environ.get("SAUCE") == "1" and bool(
        os.environ.get("SAUCE_USERNAME") and os.environ.get("SAUCE_ACCESS_KEY")
    )


def _construir_sauce_capabilities(test_name: str) -> dict:
    """Construye el diccionario de capabilities W3C / Sauce Labs para la sesión remota."""
    caps = {
        "browserName": os.environ.get("SAUCE_BROWSER", "chrome"),
        "browserVersion": os.environ.get("SAUCE_BROWSER_VERSION", "latest"),
        "platformName": os.environ.get("SAUCE_PLATFORM", "Windows 11"),
        "sauce:options": {
            "username": os.environ.get("SAUCE_USERNAME", ""),
            "accessKey": os.environ.get("SAUCE_ACCESS_KEY", ""),
            "name": test_name,
            "build": os.environ.get("BUILD_TAG", "reto5-tienda-qa-cloud"),
            "screenResolution": "1920x1080",
        },
    }
    tunnel = os.environ.get("SAUCE_TUNNEL")
    if tunnel:
        caps["sauce:options"]["tunnelName"] = tunnel
    return caps


def pytest_addoption(parser):
    parser.addoption(
        "--base-url-tienda",
        action="store",
        default=None,
        help="URL base de la app Tienda (ej. http://localhost:3000)",
    )


@pytest.fixture(scope="session")
def base_url(request):
    return (
        request.config.getoption("--base-url-tienda")
        or os.environ.get("BASE_URL")
        or "http://localhost:3000"
    )


@pytest.fixture(autouse=True)
def _reset_pedidos(base_url):
    """Reinicia los pedidos en memoria antes de cada escenario para garantizar aislamiento."""
    try:
        requests.post(f"{base_url}/api/test/reset", timeout=3)
    except requests.RequestException:
        pass
    yield


# ──────────────────────────────────────────────────────────────────
#  Enlace con Azure Test Plans (Fase 3): extrae el tag @TC<id> de cada
#  escenario Gherkin y lo escribe como propiedad <property name="test_case_id">
#  en el reporte JUnit XML para que tools/publicar_test_plan.py actualice
#  el Test Point correspondiente en Azure DevOps.
# ──────────────────────────────────────────────────────────────────
_RE_TC = re.compile(r"^TC(\d+)$", re.IGNORECASE)


def pytest_collection_modifyitems(items):
    for item in items:
        for mark in item.iter_markers():
            m = _RE_TC.match(mark.name)
            if m:
                item.user_properties.append(("test_case_id", m.group(1)))


# ──────────────────────────────────────────────────────────────────
#  Fixture principal: Actor Screenplay (Local vs Sauce Labs Cloud)
# ──────────────────────────────────────────────────────────────────
@pytest.fixture
def actor(request, playwright, base_url):
    """Entrega un Actor Screenplay conectado a un navegador local o a Sauce Labs en la nube."""
    if _usar_sauce():
        region = os.environ.get("SAUCE_REGION", "us-west-1")
        caps = _construir_sauce_capabilities(request.node.name)
        ws_endpoint = (
            f"wss://ondemand.{region}.saucelabs.com/wd/hub/playwright"
            f"?caps={quote(json.dumps(caps))}"
        )
        browser = playwright.chromium.connect(ws_endpoint)
        context = browser.new_context()
        page = context.new_page()
        yield Actor.llamado("Cliente Cloud (Sauce Labs)").que_puede(
            NavegarConElNavegador.usando(page, base_url)
        )
        # Informar a Sauce Labs si el escenario pasó o falló
        passed = not getattr(request.node, "rep_call_failed", False)
        try:
            page.evaluate(f"sauce:job-result={'passed' if passed else 'failed'}")
        except Exception:
            pass
        context.close()
        browser.close()
    else:
        # Ejecución local usando el fixture page de pytest-playwright
        page = request.getfixturevalue("page")
        yield Actor.llamado("Cliente Local").que_puede(
            NavegarConElNavegador.usando(page, base_url)
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        setattr(item, "rep_call_failed", True)
