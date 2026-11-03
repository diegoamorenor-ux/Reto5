# Reto 6 — Quality Gate de Certificación: Gobernanza de QA y Modelos de ML

- **Diplomado Ejecutivo en Automatización Inteligente de Pruebas de Software — Módulo 5 / Taller 6**
- **Autor:** Diego Moreno (`diegoamorenor-ux`)
- **Repositorio Personal Integrado:** `https://github.com/diegoamorenor-ux/Reto5/tree/main/reto6-quality-gate`
- **Referencia del Reto:** `https://github.com/dsolisp/curso/tree/main/curso6/retos/reto-practico`

---

## 1. Descripción del Reto

Este proyecto implementa un **Quality Gate automatizado en Python** que unifica en un único punto de control las métricas de **Gobernanza de Calidad de Software (Día 1)** y las métricas de **Equidad y Estabilidad de Modelos de Machine Learning de Aprobación de Crédito (Día 2)**.

El módulo [`src/quality_gate.py`](src/quality_gate.py) implementa las **6 funciones** requeridas sin librerías externas (solo `math` y biblioteca estándar) y es validado automáticamente por la suite inmutable [`tests/test_quality_gate.py`](tests/test_quality_gate.py) alcanzando **`14 passed`**.

---

## 2. Umbrales Oficiales de Certificación (`THRESHOLDS`)

| Métrica | Función en `src/quality_gate.py` | Fórmula Matemática | Umbral | Condición de Fallo | Dimensión |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Flake Rate** | `flake_rate(flaky_tests, total_tests)` | $\frac{\text{flaky\_tests}}{\text{total\_tests}}$ (`0.0` si `total == 0`) | `0.10` | Falla si **`> 0.10`** | Día 1 — Estabilidad de Suite |
| **Defect Leakage** | `defect_leakage(prod_defects, total_defects)` | $\frac{\text{prod\_defects}}{\text{total\_defects}}$ (`0.0` si `total == 0`) | `0.12` | Falla si **`> 0.12`** | Día 1 — Fuga a Producción |
| **Test Effectiveness** | `test_effectiveness(found_in_test, total_defects)` | $\frac{\text{found\_in\_test}}{\text{total\_defects}}$ (`1.0` si `total == 0`) | `0.85` | Falla si **`< 0.85`** | Día 1 — Eficacia de Detección |
| **Fairness Gap** | `fairness_gap(approval_rates)` | $\max(\text{rates}) - \min(\text{rates})$ (`0.0` si $\le 1$ región) | `0.25` | Falla si **`> 0.25`** | Día 2 — Sesgo Regional ML |
| **PSI (Drift)** | `psi(expected_pct, actual_pct)` | $\sum (a_i - e_i) \ln(a_i / e_i)$ (`0` $\rightarrow$ `0.0001`) | `0.25` | Falla si **`> 0.25`** | Día 2 — Deriva Poblacional ML |

---

## 3. Cómo Ejecutar y Validar

```bash
# 1. Instalar dependencias y sincronizar entorno (con uv o pytest en virtualenv)
uv sync

# 2. Ejecutar la suite de 14 pruebas unitarias de calificación
uv run pytest -v

# 3. Ejecutar el veredicto del Quality Gate sobre el release de ejemplo
uv run python -m src.quality_gate
```

### Salida del Veredicto (`python -m src.quality_gate`)

```json
{
  "checks": {
    "flake_rate": true,
    "defect_leakage": false,
    "test_effectiveness": true,
    "fairness_gap": true,
    "psi": true
  },
  "passed": false
}
```

---

## 4. Explicación Ejecutiva del Bloqueo del Release (En Una Frase)

> **¿Por qué se bloquea el release y quién es el dueño de la acción?**  
> El release se bloquea automáticamente (`"passed": false`) porque la tasa de fuga de defectos a producción (**`defect_leakage = 28 / 200 = 0.14`**, es decir **14%**) supera el umbral máximo permitido del **12% (`0.12`)**, a pesar de que la estabilidad de pruebas (`flake_rate = 0.09`), la efectividad (`0.86`), la equidad regional (`fairness_gap = 0.17`) y la estabilidad del modelo ML (`psi = 0.0079`) están en verde; el **dueño de la acción correctiva es el Líder de QA / Ingeniería de Calidad (junto al Tech Lead del equipo de desarrollo)**, quien debe realizar el análisis de causa raíz de los 28 bugs escapados y reforzar la cobertura de pruebas de regresión y contratos antes de autorizar el despliegue.
