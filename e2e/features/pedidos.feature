# Suite "Pedidos" de Azure Test Plans traducida a Gherkin
# Keywords en inglés, texto de los pasos en español.
Feature: Confirmar un pedido en la tienda
  Como cliente de la tienda
  quiero confirmar un pedido con un producto en el carrito
  para completar mi compra y obtener un numero de orden

  # @TC21 = ID del Test Case manual en Azure Test Plans
  @pedidos @smoke @TC21
  Scenario: Confirmar un pedido con un producto
    Given que abro la home de la tienda
    And agrego el producto 1 al carrito
    When abro el carrito y confirmo el pedido con el correo "ana@tienda-qa.com"
    Then veo el mensaje de pedido confirmado
    And el numero de pedido no esta vacio
