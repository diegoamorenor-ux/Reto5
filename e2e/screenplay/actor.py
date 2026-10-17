"""Actor: el protagonista de la prueba en el patrón Screenplay.

Un Actor posee habilidades (abilities), ejecuta tareas de negocio (intenta / attempts_to)
y responde preguntas sobre el estado observable del sistema (pregunta / asks).
"""
from typing import Any


class Actor:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self._habilidades: dict[type, Any] = {}

    @staticmethod
    def llamado(nombre: str) -> "Actor":
        return Actor(nombre)

    def que_puede(self, *habilidades) -> "Actor":
        """Dota al actor de una o varias habilidades."""
        for h in habilidades:
            self._habilidades[type(h)] = h
        return self

    def habilidad(self, tipo: type):
        """Recupera una habilidad por su tipo."""
        if tipo not in self._habilidades:
            raise AssertionError(f"{self.nombre} no tiene la habilidad {tipo.__name__}")
        return self._habilidades[tipo]

    def intenta(self, *tareas) -> "Actor":
        """Ejecuta una secuencia de tareas o interacciones en orden."""
        for t in tareas:
            t.ejecutar_como(self)
        return self

    def pregunta(self, pregunta) -> Any:
        """Evalúa una Question sobre el estado actual de la aplicación."""
        return pregunta.responder_como(self)
