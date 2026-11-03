"""Quality gate — Reto práctico de Certificación 6.

Implementa las funciones marcadas con TODO. La suite en
tests/test_quality_gate.py valida cada una: cuando todo esté bien
implementado vas a ver 14 passed.

Regla del reto: no modifiques THRESHOLDS ni los tests.
"""

import json
import math

# Umbrales del curso (Día 1 + Día 2)
THRESHOLDS = {
    "flake_rate": 0.10,          # falla si >
    "defect_leakage": 0.12,      # falla si >
    "test_effectiveness": 0.85,  # falla si <
    "fairness_gap": 0.25,        # falla si >
    "psi": 0.25,                 # falla si >
}


def flake_rate(flaky_tests: int, total_tests: int) -> float:
    """Tests flaky / tests ejecutados.

    Caso borde: si total_tests es 0, devuelve 0.0 (no hay nada que medir).
    Ejemplo: flake_rate(9, 100) -> 0.09
    """
    if total_tests == 0:
        return 0.0
    return flaky_tests / total_tests


def defect_leakage(prod_defects: int, total_defects: int) -> float:
    """Defectos encontrados en producción / defectos totales.

    Caso borde: si total_defects es 0, devuelve 0.0 (sin defectos no hay fuga).
    Ejemplo: defect_leakage(4, 25) -> 0.16
    """
    if total_defects == 0:
        return 0.0
    return prod_defects / total_defects


def test_effectiveness(defects_found_in_test: int, total_defects: int) -> float:
    """Defectos hallados en testing / defectos totales.

    Caso borde: si total_defects es 0, devuelve 1.0 (la red no dejó pasar nada).
    Ejemplo: test_effectiveness(17, 20) -> 0.85
    """
    if total_defects == 0:
        return 1.0
    return defects_found_in_test / total_defects


def fairness_gap(approval_rates: dict[str, float]) -> float:
    """Diferencia entre la tasa de aprobación más alta y la más baja.

    approval_rates es un dict región -> tasa, ej.: {"north": 0.80, "south": 0.55}.
    Caso borde: con 0 o 1 región, devuelve 0.0 (no hay con quién comparar).
    Ejemplo: {"north": 0.80, "south": 0.55} -> 0.25
    """
    if len(approval_rates) <= 1:
        return 0.0
    rates = approval_rates.values()
    return max(rates) - min(rates)


def psi(expected_pct: list[float], actual_pct: list[float]) -> float:
    """Population Stability Index entre dos distribuciones por bucket.

    PSI = Σ (actual_i − esperado_i) × ln(actual_i / esperado_i)

    Ambas listas traen proporciones por bucket (suman ~1.0) y tienen el
    mismo largo. Para evitar división por cero o ln(0): si algún valor es 0,
    reemplázalo por 0.0001 antes de calcular.
    Pista: math.log es el logaritmo natural (ln).
    Ejemplo: psi([0.5, 0.5], [0.5, 0.5]) -> 0.0
    """
    total = 0.0
    for exp, act in zip(expected_pct, actual_pct):
        e = 0.0001 if exp == 0 else exp
        a = 0.0001 if act == 0 else act
        total += (a - e) * math.log(a / e)
    return total


def quality_gate(metrics: dict[str, float]) -> dict:
    """Evalúa las 5 métricas contra THRESHOLDS y decide el release.

    metrics trae exactamente estas llaves (valores ya calculados):
    flake_rate, defect_leakage, test_effectiveness, fairness_gap, psi.

    Devuelve: {"checks": {<métrica>: bool, ...}, "passed": bool}
    - checks[m] es True si la métrica está dentro del umbral.
    - Ojo con la dirección: effectiveness falla por DEBAJO del umbral;
      las otras cuatro fallan por ENCIMA.
    - El valor exactamente igual al umbral PASA (falla solo si lo cruza).
    - passed es True solo si TODOS los checks son True.
    """
    checks = {
        "flake_rate": metrics["flake_rate"] <= THRESHOLDS["flake_rate"],
        "defect_leakage": metrics["defect_leakage"] <= THRESHOLDS["defect_leakage"],
        "test_effectiveness": metrics["test_effectiveness"] >= THRESHOLDS["test_effectiveness"],
        "fairness_gap": metrics["fairness_gap"] <= THRESHOLDS["fairness_gap"],
        "psi": metrics["psi"] <= THRESHOLDS["psi"],
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
    }


if __name__ == "__main__":
    # Release de ejemplo: todo sano excepto el leakage (28 de 200 bugs en prod)
    release = {
        "flake_rate": flake_rate(18, 200),
        "defect_leakage": defect_leakage(28, 200),
        "test_effectiveness": test_effectiveness(172, 200),
        "fairness_gap": fairness_gap(
            {"north": 0.78, "south": 0.61, "east": 0.70, "west": 0.66}
        ),
        "psi": psi(
            [0.25, 0.25, 0.25, 0.25],
            [0.22, 0.24, 0.27, 0.27],
        ),
    }
    print(json.dumps(quality_gate(release), indent=2))
