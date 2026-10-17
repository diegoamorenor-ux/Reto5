"""Enlaza el feature de Carrito con sus step definitions."""
from pytest_bdd import scenarios

from steps.steps_comunes import *  # noqa: F401,F403

scenarios("carrito.feature")
