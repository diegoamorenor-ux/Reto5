"""Steps compartidos entre los features (Given/When/Then reutilizables con Screenplay)."""
from pytest_bdd import given, when, then, parsers

from screenplay.tasks import (
    AbrirElCatalogo,
    FiltrarPorCategoria,
    BuscarProductoPorTexto,
    AgregarProductoAlCarrito,
    AbrirElCarrito,
    ConfirmarPedido,
)
from screenplay.questions import (
    ContadorCarrito,
    ProductosVisibles,
    CategoriasVisibles,
    MensajeSinResultadosVisible,
    MensajeCarritoVacioVisible,
    CantidadEnFilaDelCarrito,
    NumeroDePedido,
    MensajeDeExitoVisible,
)


# ── GIVEN ──────────────────────────────────────────────────────────
@given("que abro la home de la tienda")
def abrir_home(actor):
    actor.intenta(AbrirElCatalogo())


# ── WHEN ───────────────────────────────────────────────────────────
@when(parsers.parse('filtro el catalogo por la categoria "{categoria}"'))
def filtrar_categoria(actor, categoria):
    actor.intenta(FiltrarPorCategoria.llamada(categoria))


@when(parsers.parse('busco en el catalogo el termino "{termino}"'))
def buscar_termino(actor, termino):
    actor.intenta(BuscarProductoPorTexto.con_termino(termino))


@when(parsers.parse("agrego el producto {producto_id:d} al carrito"))
@given(parsers.parse("agrego el producto {producto_id:d} al carrito"))
def agregar_producto(actor, producto_id):
    actor.intenta(AgregarProductoAlCarrito.con_id(producto_id))


@when("abro la vista del carrito")
def abrir_vista_carrito(actor):
    actor.intenta(AbrirElCarrito())


@when(parsers.parse('abro el carrito y confirmo el pedido con el correo "{correo}"'))
def abrir_y_confirmar(actor, correo):
    actor.intenta(AbrirElCarrito(), ConfirmarPedido.con_correo(correo))


# ── THEN ───────────────────────────────────────────────────────────
@then(parsers.parse('solo veo productos de la categoria "{categoria}"'))
def solo_categoria(actor, categoria):
    categorias = actor.pregunta(CategoriasVisibles.lista())
    assert len(categorias) > 0, "No se encontraron tarjetas visibles"
    assert all(c == categoria for c in categorias), (
        f"Se esperaban solo '{categoria}', pero hay: {set(categorias)}"
    )


@then("la cantidad de productos visibles es mayor que cero")
def hay_productos(actor):
    assert actor.pregunta(ProductosVisibles.cantidad()) > 0


@then(parsers.parse("la cantidad de productos visibles es {cantidad_esperada:d}"))
def cantidad_exacta_productos(actor, cantidad_esperada):
    assert actor.pregunta(ProductosVisibles.cantidad()) == cantidad_esperada


@then("veo el mensaje de que no hay productos para ese filtro")
def mensaje_sin_resultados(actor):
    assert actor.pregunta(MensajeSinResultadosVisible.estado()) is True


@then(parsers.parse("el contador del carrito muestra {esperado:d}"))
def contador_carrito(actor, esperado):
    assert actor.pregunta(ContadorCarrito.valor()) == esperado


@then(parsers.parse("la fila del producto {producto_id:d} en el carrito muestra cantidad {cantidad:d}"))
def cantidad_en_fila(actor, producto_id, cantidad):
    assert actor.pregunta(CantidadEnFilaDelCarrito.del_producto(producto_id)) == cantidad


@then("veo el mensaje de carrito vacio")
def mensaje_carrito_vacio(actor):
    assert actor.pregunta(MensajeCarritoVacioVisible.estado()) is True


@then("veo el mensaje de pedido confirmado")
def mensaje_confirmado(actor):
    assert actor.pregunta(MensajeDeExitoVisible.estado()) is True


@then("el numero de pedido no esta vacio")
def numero_pedido(actor):
    assert actor.pregunta(NumeroDePedido.texto()) != ""
