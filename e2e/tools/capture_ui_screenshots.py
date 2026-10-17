#!/usr/bin/env python3
"""Captura capturas de pantalla reales (PNG) de la interfaz web de Tienda QA
usando Playwright para el Documento de Soporte del Reto 5.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests

BASE_URL = "http://localhost:3000"
OUT_DIR = Path(__file__).resolve().parents[2] / "evidencias"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    try:
        requests.post(f"{BASE_URL}/api/test/reset", timeout=3)
    except Exception:
        pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 820})
        page = context.new_page()

        # 1. Home / Catálogo completo (24 productos con Faker seed 12345)
        page.goto(BASE_URL)
        page.wait_for_selector('[data-testid="grid-productos"] .card')
        page.screenshot(path=str(OUT_DIR / "ui_01_catalogo_completo.png"), full_page=False)

        # 2. Catálogo filtrado por categoría "hogar" (@TC20)
        page.get_by_test_id("filtro-categoria").select_option("hogar")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT_DIR / "ui_02_catalogo_filtrado_hogar.png"), full_page=False)

        # 3. Caso de borde propuesto por IA (@TC22): Búsqueda sin coincidencias
        page.get_by_test_id("filtro-categoria").select_option("")
        page.get_by_test_id("busqueda").fill("xyzinexistente999")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT_DIR / "ui_03_borde_ia_sin_resultados.png"), full_page=False)

        # 4. Caso de borde propuesto por IA (@TC24): Carrito vacío
        page.get_by_test_id("busqueda").fill("")
        page.get_by_test_id("abrir-carrito").click()
        page.wait_for_selector('[data-testid="carrito-vacio"]')
        page.screenshot(path=str(OUT_DIR / "ui_04_borde_ia_carrito_vacio.png"), full_page=False)

        # 5. Caso de borde propuesto por IA (@TC23): Acumulación en el carrito (2 unidades del producto 1)
        page.get_by_test_id("logo").click()
        page.wait_for_selector('[data-testid="grid-productos"] .card')
        page.get_by_test_id("agregar-1").click()
        page.get_by_test_id("agregar-1").click()
        page.get_by_test_id("abrir-carrito").click()
        page.wait_for_selector('[data-testid="carrito-tabla"]')
        page.screenshot(path=str(OUT_DIR / "ui_05_carrito_acumulado_ia.png"), full_page=False)

        # 6. Confirmación de pedido (@TC21)
        page.get_by_test_id("input-email").fill("ana@tienda-qa.com")
        page.get_by_test_id("confirmar-pedido").click()
        page.wait_for_selector('[data-testid="vista-exito"].activa')
        page.screenshot(path=str(OUT_DIR / "ui_06_pedido_confirmado.png"), full_page=False)

        context.close()
        browser.close()
    print("Capturas UI generadas exitosamente en evidencias/")


if __name__ == "__main__":
    main()
