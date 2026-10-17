# Suite "Catálogo" de Azure Test Plans traducida a Gherkin + Escenario de Borde generado con IA (Claude + MCP Playwright)
# Keywords en inglés (Feature/Scenario/Given/When/Then/And), texto de pasos en español.
Feature: Filtrar y buscar en el catalogo de la tienda
  Como cliente de la tienda
  quiero filtrar por categoria y buscar productos por texto
  para encontrar rapidamente lo que necesito o saber si no hay coincidencias

  # @TC20 = ID del Test Case manual en Azure Test Plans
  @catalogo @smoke @TC20
  Scenario: Filtrar productos por categoria Hogar
    Given que abro la home de la tienda
    When filtro el catalogo por la categoria "hogar"
    Then solo veo productos de la categoria "hogar"
    And la cantidad de productos visibles es mayor que cero

  # @TC22 = Escenario de borde propuesto y generado con IA (Claude + MCP Playwright)
  @catalogo @borde @ia @TC22
  Scenario: Buscar un producto inexistente muestra mensaje de sin resultados
    Given que abro la home de la tienda
    When busco en el catalogo el termino "xyzinexistente999"
    Then la cantidad de productos visibles es 0
    And veo el mensaje de que no hay productos para ese filtro
