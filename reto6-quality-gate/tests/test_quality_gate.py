"""Suite del reto práctico — NO MODIFICAR.

Cuando las 6 funciones estén bien implementadas: 14 passed.
"""

import math

import pytest

from src.quality_gate import (
    THRESHOLDS,
    defect_leakage,
    fairness_gap,
    flake_rate,
    psi,
    quality_gate,
)

# Alias: si se importa con su nombre real, pytest la confundiría con un test
from src.quality_gate import test_effectiveness as effectiveness

# Métricas de un release sano (todas dentro del umbral)
HEALTHY = {
    "flake_rate": 0.05,
    "defect_leakage": 0.08,
    "test_effectiveness": 0.90,
    "fairness_gap": 0.10,
    "psi": 0.04,
}


def test_flake_rate_basico():
    assert flake_rate(9, 100) == pytest.approx(0.09)
    assert flake_rate(18, 200) == pytest.approx(0.09)


def test_flake_rate_sin_tests():
    assert flake_rate(0, 0) == 0.0


def test_defect_leakage_basico():
    assert defect_leakage(4, 25) == pytest.approx(0.16)
    assert defect_leakage(3, 20) == pytest.approx(0.15)


def test_defect_leakage_sin_defectos():
    assert defect_leakage(0, 0) == 0.0


def test_effectiveness_basico():
    assert effectiveness(17, 20) == pytest.approx(0.85)


def test_effectiveness_sin_defectos_es_uno():
    assert effectiveness(0, 0) == 1.0


def test_fairness_gap_ejemplo_del_curso():
    # Norte 80% vs Sur 55% → gap 0.25 (el caso del Bloque A)
    rates = {"north": 0.80, "south": 0.55, "east": 0.70, "west": 0.66}
    assert fairness_gap(rates) == pytest.approx(0.25)


def test_fairness_gap_una_region():
    assert fairness_gap({"north": 0.80}) == 0.0
    assert fairness_gap({}) == 0.0


def test_psi_distribuciones_identicas():
    assert psi([0.25, 0.25, 0.25, 0.25], [0.25, 0.25, 0.25, 0.25]) == pytest.approx(0.0)


def test_psi_drift_evidente():
    # Corrimiento fuerte de la distribución → PSI > 0.25
    value = psi([0.40, 0.30, 0.20, 0.10], [0.10, 0.20, 0.30, 0.40])
    assert value > 0.25


def test_psi_maneja_bucket_en_cero():
    # Un bucket en 0 no debe reventar con ln(0) ni división por cero
    value = psi([0.50, 0.50, 0.0], [0.40, 0.40, 0.20])
    assert math.isfinite(value)
    assert value > 0


def test_gate_release_sano_pasa():
    result = quality_gate(HEALTHY)
    assert result["passed"] is True
    assert all(result["checks"].values())


def test_gate_bloquea_solo_lo_roto():
    # Leakage roto (0.16 > 0.12); el resto sano → passed False, un solo check en False
    metrics = dict(HEALTHY, defect_leakage=0.16)
    result = quality_gate(metrics)
    assert result["passed"] is False
    assert result["checks"]["defect_leakage"] is False
    fallidos = [name for name, ok in result["checks"].items() if not ok]
    assert fallidos == ["defect_leakage"]


def test_gate_valor_igual_al_umbral_pasa():
    # Exactamente en el umbral NO es cruzarlo: debe pasar
    metrics = {
        "flake_rate": THRESHOLDS["flake_rate"],
        "defect_leakage": THRESHOLDS["defect_leakage"],
        "test_effectiveness": THRESHOLDS["test_effectiveness"],
        "fairness_gap": THRESHOLDS["fairness_gap"],
        "psi": THRESHOLDS["psi"],
    }
    result = quality_gate(metrics)
    assert result["passed"] is True
