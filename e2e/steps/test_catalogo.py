"""Enlaza el feature de Catálogo con sus step definitions."""
from pytest_bdd import scenarios

from steps.steps_comunes import *  # noqa: F401,F403

scenarios("catalogo.feature")
