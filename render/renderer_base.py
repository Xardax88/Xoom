"""
Interfaz base para renderers.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Iterable, Optional

from core.map_data import MapData
from core.player import Player
from core.types import Segment


class IRenderer(ABC):
    @abstractmethod
    def is_running(self) -> bool:
        """Devuelve True si el renderizador (p. ej. la ventana) sigue activo."""
        ...

    @abstractmethod
    def poll_input(self) -> Dict[str, Any]:
        """
        Sondea y procesa la entrada del usuario y la devuelve en un formato
        estandarizado que el juego pueda entender.
        """
        ...

    @abstractmethod
    def draw_frame(
        self,
        map_data: MapData,
        player: Player,
        visible_segments: Optional[Iterable[Segment]] = None,
    ) -> None:
        """
        Dibuja un único fotograma en el búfer trasero de la pantalla.
        No se encarga de mostrarlo.
        """
        ...

    @abstractmethod
    def dispatch_events(self) -> None:
        """
        Procesa los eventos pendientes de la ventana (movimiento del ratón,
        clics, etc.). Esencial para que la aplicación no se bloquee.
        """
        ...

    @abstractmethod
    def flip_buffers(self) -> None:
        """
        Intercambia los búferes de la pantalla para mostrar el fotograma
        renderizado.
        """
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Limpia los recursos del renderizador (p. ej. al cerrar)."""
        ...

    @abstractmethod
    def draw_main_menu(self, options, selected_index) -> None:
        """
        Dibuja el menú principal del juego con las opciones disponibles.
        `options` es una lista de cadenas y `selected_index` indica cuál
        opción está seleccionada.
        """
        ...
