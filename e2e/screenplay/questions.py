"""Questions: lo que el Actor OBSERVA para verificar el estado de la aplicación."""
from .abilities import NavegarConElNavegador


def _page(actor):
    return actor.habilidad(NavegarConElNavegador).page


class ContadorCarrito:
    """Número que muestra el contador del carrito en el encabezado."""

    @staticmethod
    def valor() -> "ContadorCarrito":
        return ContadorCarrito()

    def responder_como(self, actor) -> int:
        texto = _page(actor).get_by_test_id("contador-carrito").inner_text()
        return int(texto.strip())


class ProductosVisibles:
    """Cantidad de tarjetas de producto visibles actualmente en el catálogo."""

    @staticmethod
    def cantidad() -> "ProductosVisibles":
        return ProductosVisibles()

    def responder_como(self, actor) -> int:
        return _page(actor).locator('[data-testid="grid-productos"] .card').count()


class CategoriasVisibles:
    """Lista de categorías (atributo data-categoria) de las tarjetas visibles."""

    @staticmethod
    def lista() -> "CategoriasVisibles":
        return CategoriasVisibles()

    def responder_como(self, actor) -> list[str]:
        tarjetas = _page(actor).locator('[data-testid="grid-productos"] .card')
        n = tarjetas.count()
        return [tarjetas.nth(i).get_attribute("data-categoria") for i in range(n)]


class MensajeSinResultadosVisible:
    """True si el mensaje 'No hay productos para ese filtro.' está visible (Caso de borde IA)."""

    @staticmethod
    def estado() -> "MensajeSinResultadosVisible":
        return MensajeSinResultadosVisible()

    def responder_como(self, actor) -> bool:
        return _page(actor).get_by_test_id("sin-resultados").is_visible()


class MensajeCarritoVacioVisible:
    """True si al abrir el carrito sin productos se muestra 'Tu carrito esta vacio.' (Caso de borde IA)."""

    @staticmethod
    def estado() -> "MensajeCarritoVacioVisible":
        return MensajeCarritoVacioVisible()

    def responder_como(self, actor) -> bool:
        return _page(actor).get_by_test_id("carrito-vacio").is_visible()


class CantidadEnFilaDelCarrito:
    """Cantidad acumulada para un producto específico en la tabla del carrito (Caso de borde IA)."""

    def __init__(self, producto_id: int):
        self.producto_id = producto_id

    @staticmethod
    def del_producto(producto_id: int) -> "CantidadEnFilaDelCarrito":
        return CantidadEnFilaDelCarrito(producto_id)

    def responder_como(self, actor) -> int:
        fila = _page(actor).get_by_test_id(f"fila-{self.producto_id}")
        celda_cantidad = fila.locator("td").nth(1)
        return int(celda_cantidad.inner_text().strip())


class TotalDelCarrito:
    """Texto del total mostrado en el carrito (ej. 'Total: $123.00')."""

    @staticmethod
    def texto() -> "TotalDelCarrito":
        return TotalDelCarrito()

    def responder_como(self, actor) -> str:
        return _page(actor).get_by_test_id("carrito-total").inner_text().strip()


class NumeroDePedido:
    """Número de pedido mostrado en la pantalla de confirmación."""

    @staticmethod
    def texto() -> "NumeroDePedido":
        return NumeroDePedido()

    def responder_como(self, actor) -> str:
        return _page(actor).get_by_test_id("numero-pedido").inner_text().strip()


class MensajeDeExitoVisible:
    """True si la pantalla de confirmación de pedido es visible."""

    @staticmethod
    def estado() -> "MensajeDeExitoVisible":
        return MensajeDeExitoVisible()

    def responder_como(self, actor) -> bool:
        return _page(actor).get_by_test_id("mensaje-exito").is_visible()
