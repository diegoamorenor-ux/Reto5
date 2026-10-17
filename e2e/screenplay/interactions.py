"""Interactions: acciones atómicas de bajo nivel sobre la Page de Playwright.

Son los bloques de construcción con los que se componen las Tasks de negocio.
"""
from .abilities import NavegarConElNavegador


def _page(actor):
    return actor.habilidad(NavegarConElNavegador).page


def _base(actor):
    return actor.habilidad(NavegarConElNavegador).base_url


class Abrir:
    """Abre una ruta relativa a la base_url (ej. '/')."""

    def __init__(self, ruta: str):
        self.ruta = ruta

    @staticmethod
    def la_pagina(ruta: str = "/") -> "Abrir":
        return Abrir(ruta)

    def ejecutar_como(self, actor):
        _page(actor).goto(_base(actor) + self.ruta)


class HacerClic:
    """Hace clic sobre un elemento identificado por data-testid."""

    def __init__(self, testid: str):
        self.testid = testid

    @staticmethod
    def en(testid: str) -> "HacerClic":
        return HacerClic(testid)

    def ejecutar_como(self, actor):
        _page(actor).get_by_test_id(self.testid).click()


class Escribir:
    """Escribe texto en un campo identificado por data-testid."""

    def __init__(self, texto: str, testid: str = ""):
        self.texto = texto
        self.testid = testid

    @staticmethod
    def el_texto(texto: str) -> "Escribir":
        return Escribir(texto)

    def en(self, testid: str) -> "Escribir":
        self.testid = testid
        return self

    def ejecutar_como(self, actor):
        campo = _page(actor).get_by_test_id(self.testid)
        campo.fill(self.texto)


class Seleccionar:
    """Selecciona una opción por valor en un <select> identificado por data-testid."""

    def __init__(self, valor: str, testid: str = ""):
        self.valor = valor
        self.testid = testid

    @staticmethod
    def el_valor(valor: str) -> "Seleccionar":
        return Seleccionar(valor)

    def en(self, testid: str) -> "Seleccionar":
        self.testid = testid
        return self

    def ejecutar_como(self, actor):
        _page(actor).get_by_test_id(self.testid).select_option(self.valor)
