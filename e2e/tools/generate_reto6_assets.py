"""
Genera las capturas de pantalla PNG de evidencia del Reto 6 (14 failed, 14 passed, y salida del Quality Gate),
exporta DOCUMENTO_DE_SOPORTE_RETO6.html y DOCUMENTO_DE_SOPORTE_RETO6.pdf,
sincroniza todo hacia ../Taller6 y publica el commit en GitHub (Reto5).
"""
from __future__ import annotations
import html
import shutil
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

import export_support_pdf
from generate_evidence_assets import make_card_html, render_html_to_png

ROOT = Path(__file__).resolve().parents[2]
RETO6_DIR = ROOT / "reto6-quality-gate"
EVID_DIR = RETO6_DIR / "evidencias"
LOGS_DIR = EVID_DIR / "logs"
TALLER6_EXT_DIR = ROOT.parent / "Taller6"


def build_reto6_images():
    nested = RETO6_DIR / "reto6-quality-gate"
    if nested.exists():
        shutil.rmtree(nested)

    log_failed = (LOGS_DIR / "01_pytest_inicial_14_failed.txt").read_text(encoding="utf-8")
    log_passed = (LOGS_DIR / "02_pytest_final_14_passed.txt").read_text(encoding="utf-8")
    # Compact long rootdir path in log_passed so every test fits on a single line
    log_passed_clean = log_passed.replace(
        "/Users/diegomoreno/Desktop/Diplomado Ejecutivo en Automatización Inteligente de Pruebas de Software/Modulo5/taller5/reto6-quality-gate",
        "~/Modulo5/Taller6",
    ).replace(
        "/Users/diegomoreno/Desktop/Diplomado Ejecutivo en Automatización Inteligente de Pruebas de Software/Modulo5/taller5/e2e/.venv/bin/python3.13",
        "~/.venv/bin/python3.13",
    )
    log_failed_clean = log_failed.replace(
        "/Users/diegomoreno/Desktop/Diplomado Ejecutivo en Automatización Inteligente de Pruebas de Software/Modulo5/taller5/reto6-quality-gate/",
        "",
    )
    log_gate = (LOGS_DIR / "03_quality_gate_salida.json").read_text(encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1220, "height": 1400})

        # 1. Baseline 14 failed
        body_failed = f"""
        <div class="panel">
          <h4>Ejecución Inicial del Esqueleto (uv run pytest -v) -> 14 failed</h4>
          <pre>$ uv run pytest -v
{html.escape(log_failed_clean.strip())}</pre>
        </div>
        """
        render_html_to_png(
            page,
            make_card_html(
                "RETO 6 — Línea Base Inicial (Esqueleto con TODOs sin implementar)",
                "curso6/retos/reto-practico | uv run pytest -v -> 14 failed (NotImplementedError)",
                "BASELINE: 14 FAILED",
                "#d97706",
                body_failed,
            ),
            EVID_DIR / "01_baseline_14_failed.png",
        )

        # 2. Final 14 passed
        body_passed = f"""
        <div class="grid-2">
          <div class="panel">
            <h4>Suite de Calificación Automática (uv run pytest -v) -> 14 passed</h4>
            <pre>$ uv run pytest -v
{html.escape(log_passed_clean.strip())}</pre>
          </div>
          <div class="panel">
            <h4>Resumen de las 6 Funciones Calificadas en Verde</h4>
            <table>
              <tr><th>Función</th><th>Tests Validados</th><th>Estado</th></tr>
              <tr><td><code>flake_rate</code></td><td><code>test_flake_rate_basico</code>, <code>test_flake_rate_sin_tests</code></td><td><span class="ok">2/2 PASSED</span></td></tr>
              <tr><td><code>defect_leakage</code></td><td><code>test_defect_leakage_basico</code>, <code>test_defect_leakage_sin_defectos</code></td><td><span class="ok">2/2 PASSED</span></td></tr>
              <tr><td><code>test_effectiveness</code></td><td><code>test_effectiveness_basico</code>, <code>test_effectiveness_sin_defectos_es_uno</code></td><td><span class="ok">2/2 PASSED</span></td></tr>
              <tr><td><code>fairness_gap</code></td><td><code>test_fairness_gap_ejemplo_del_curso</code>, <code>test_fairness_gap_una_region</code></td><td><span class="ok">2/2 PASSED</span></td></tr>
              <tr><td><code>psi</code></td><td><code>test_psi_distribuciones_identicas</code>, <code>test_psi_drift_evidente</code>, <code>test_psi_maneja_bucket_en_cero</code></td><td><span class="ok">3/3 PASSED</span></td></tr>
              <tr><td><code>quality_gate</code></td><td><code>test_gate_release_sano_pasa</code>, <code>test_gate_bloquea_solo_lo_roto</code>, <code>test_gate_valor_igual_al_umbral_pasa</code></td><td><span class="ok">3/3 PASSED</span></td></tr>
            </table>
          </div>
        </div>
        """
        render_html_to_png(
            page,
            make_card_html(
                "RETO 6 — Calificación Automática Superada: 14 PASSED (100% en Verde)",
                "src/quality_gate.py | tests/test_quality_gate.py (sin modificaciones) | Python 3.13 + pytest",
                "14 PASSED IN 0.04s — SCORE 100%",
                "#059669",
                body_passed,
            ),
            EVID_DIR / "02_final_14_passed.png",
        )

        # 3. Salida del Quality Gate (Release bloqueado por defect_leakage 0.14 > 0.12)
        body_gate = f"""
        <div class="stage-bar">
          <div class="stage pass"><div class="ok">✓ flake_rate</div><div class="muted">0.0900 &le; 0.10 (OK)</div></div>
          <div class="stage fail-stage"><div class="fail">✗ defect_leakage</div><div class="muted">0.1400 &gt; 0.12 (FALLA)</div></div>
          <div class="stage pass"><div class="ok">✓ test_effectiveness</div><div class="muted">0.8600 &ge; 0.85 (OK)</div></div>
          <div class="stage pass"><div class="ok">✓ fairness_gap</div><div class="muted">0.1700 &le; 0.25 (OK)</div></div>
          <div class="stage pass"><div class="ok">✓ psi (drift)</div><div class="muted">0.0079 &le; 0.25 (OK)</div></div>
        </div>
        <div class="grid-2">
          <div class="panel">
            <h4>Salida Oficial: uv run python -m src.quality_gate</h4>
            <pre>$ uv run python -m src.quality_gate
{html.escape(log_gate.strip())}</pre>
          </div>
          <div class="panel">
            <h4>Diagnóstico Ejecutivo del Bloqueo</h4>
            <p style="font-size:13px;line-height:1.55;color:#e2e8f0;margin-top:6px;">
              <strong style="color:#f87171;">¿Por qué se bloquea el release?</strong><br>
              El release se bloquea automáticamente (<code>"passed": false</code>) porque <strong>28 de los 200 defectos llegaron a producción</strong>, elevando el <code>defect_leakage</code> a <strong>0.14 (14%)</strong> por encima del umbral máximo permitido de <strong>0.12 (12%)</strong>.<br><br>
              <strong style="color:#38bdf8;">¿Quién es el dueño de la acción?</strong><br>
              El <strong>Líder de QA / Ingeniería de Calidad</strong> (junto al Tech Lead de Desarrollo), quien debe ejecutar el RCA sobre los 28 bugs escapados y reforzar la suite de regresión antes de reintentar el despliegue.
            </p>
          </div>
        </div>
        """
        render_html_to_png(
            page,
            make_card_html(
                "RETO 6 — Veredicto del Quality Gate sobre Release de Ejemplo (Bloqueado por Defect Leakage)",
                "uv run python -m src.quality_gate | defect_leakage = 28/200 = 0.14 > 0.12 -> passed: false",
                "RELEASE BLOQUEADO (PASSED: FALSE)",
                "#dc2626",
                body_gate,
            ),
            EVID_DIR / "03_quality_gate_veredicto.png",
        )

        browser.close()


def build_reto6_html_and_pdf():
    # Reuse export_support_pdf logic with RETO6_DIR as base
    old_root = export_support_pdf.ROOT
    export_support_pdf.ROOT = RETO6_DIR
    export_support_pdf.MD_PATH = RETO6_DIR / "DOCUMENTO_DE_SOPORTE_RETO6.md"
    export_support_pdf.HTML_PATH = RETO6_DIR / "DOCUMENTO_DE_SOPORTE_RETO6.html"
    export_support_pdf.PDF_PATH = RETO6_DIR / "DOCUMENTO_DE_SOPORTE_RETO6.pdf"
    try:
        export_support_pdf.main()
    finally:
        export_support_pdf.ROOT = old_root


def sync_to_taller6_folder():
    TALLER6_EXT_DIR.mkdir(parents=True, exist_ok=True)
    for item in RETO6_DIR.iterdir():
        dest = TALLER6_EXT_DIR / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    print(f"Sincronizado Reto 6 completo en: {TALLER6_EXT_DIR}")


if __name__ == "__main__":
    build_reto6_images()
    build_reto6_html_and_pdf()
    sync_to_taller6_folder()
    subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
    subprocess.run(
        ["git", "commit", "-m", "feat(reto6): implementar Quality Gate Gobernanza QA + ML (14 passed) y documentacion de soporte"],
        cwd=ROOT,
        check=True,
    )
    push = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, text=True, capture_output=True)
    print(push.stdout)
    print(push.stderr)

