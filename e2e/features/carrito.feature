# Suite "Carrito" de Azure Test Plans traducida a Gherkin + Casos de Borde generados con IA (Claude + MCP Playwright)
# Keywords en inglés, texto de los pasos en español.
Feature: Gestionar productos en el carrito de compras
  Como cliente de la tienda
  quiero agregar productos al carrito y consultar su estado
  para revisar las cantidades acumuladas antes de confirmar mi compra

  # @TC19 = ID del Test Case manual en Azure Test Plans
  @carrito @smoke @TC19
  Scenario: Agregar un producto al carrito incrementa el contador
    Given que abro la home de la tienda
    When agrego el producto 1 al carrito
    Then el contador del carrito muestra 1

  # @TC23 = Caso de borde propuesto con IA (Reto Extra): acumulación del mismo ítem
  @carrito @borde @ia @TC23
  Scenario: Agregar el mismo producto dos veces acumula la cantidad en el carrito
    Given que abro la home de la tienda
    When agrego el producto 1 al carrito
    And agrego el producto 1 al carrito
    And abro la vista del carrito
    Then el contador del carrito muestra 2
    And la fila del producto 1 en el carrito muestra cantidad 2

  # @TC24 = Caso de borde propuesto con IA (Reto Extra): consulta de carrito vacío
  @carrito @borde @ia @TC24
  Scenario: Abrir el carrito sin productos muestra mensaje de carrito vacio
    Given que abro la home de la tienda
    When abro la vista del carrito
    Then veo el mensaje de carrito vacio
