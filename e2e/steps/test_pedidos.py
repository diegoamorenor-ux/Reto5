"""Enlaza el feature de Pedidos con sus step definitions."""
from pytest_bdd import scenarios

from steps.steps_comunes import *  # noqa: F401,F403

scenarios("pedidos.feature")
