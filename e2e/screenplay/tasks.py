"""Tasks: acciones de negocio de alto nivel compuestas por Interactions."""
from .interactions import Abrir, HacerClic, Escribir, Seleccionar
from .abilities import NavegarConElNavegador


class AbrirElCatalogo:
    def ejecutar_como(self, actor):
        actor.intenta(Abrir.la_pagina("/"))
        page = actor.habilidad(NavegarConElNavegador).page
        page.wait_for_selector('[data-testid="grid-productos"] .card', timeout=10000)


class FiltrarPorCategoria:
    def __init__(self, categoria: str):
        self.categoria = categoria

    @staticmethod
    def llamada(categoria: str) -> "FiltrarPorCategoria":
        return FiltrarPorCategoria(categoria)

    def ejecutar_como(self, actor):
        actor.intenta(Seleccionar.el_valor(self.categoria).en("filtro-categoria"))


class BuscarProductoPorTexto:
    """Task generada con IA + MCP de Playwright para probar el buscador del catálogo."""

    def __init__(self, termino: str):
        self.termino = termino

    @staticmethod
    def con_termino(termino: str) -> "BuscarProductoPorTexto":
        return BuscarProductoPorTexto(termino)

    def ejecutar_como(self, actor):
        actor.intenta(Escribir.el_texto(self.termino).en("busqueda"))


class AgregarProductoAlCarrito:
    def __init__(self, producto_id: int):
        self.producto_id = producto_id

    @staticmethod
    def con_id(producto_id: int) -> "AgregarProductoAlCarrito":
        return AgregarProductoAlCarrito(producto_id)

    def ejecutar_como(self, actor):
        actor.intenta(HacerClic.en(f"agregar-{self.producto_id}"))


class AbrirElCarrito:
    def ejecutar_como(self, actor):
        actor.intenta(HacerClic.en("abrir-carrito"))
        page = actor.habilidad(NavegarConElNavegador).page
        page.wait_for_selector('[data-testid="vista-carrito"].activa', timeout=10000)


class ConfirmarPedido:
    def __init__(self, correo: str):
        self.correo = correo

    @staticmethod
    def con_correo(correo: str) -> "ConfirmarPedido":
        return ConfirmarPedido(correo)

    def ejecutar_como(self, actor):
        page = actor.habilidad(NavegarConElNavegador).page
        page.wait_for_selector('[data-testid="confirmar-pedido"]', timeout=10000)
        actor.intenta(
            Escribir.el_texto(self.correo).en("input-email"),
            HacerClic.en("confirmar-pedido"),
        )
        page.wait_for_selector('[data-testid="vista-exito"].activa', timeout=10000)
