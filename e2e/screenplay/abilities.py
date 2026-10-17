"""Abilities: lo que un Actor PUEDE hacer en el patrón Screenplay."""
from playwright.sync_api import Page


class NavegarConElNavegador:
    """Habilidad de interactuar con un navegador web (Page de Playwright).

    Almacena la instancia de Page y la URL base de la aplicación bajo prueba.
    """

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def usando(page: Page, base_url: str) -> "NavegarConElNavegador":
        return NavegarConElNavegador(page, base_url)
