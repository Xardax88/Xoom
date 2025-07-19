#########################################################################
# render/renderer.py - Renderizador principal
#########################################################################

import pygame
from typing import List, Tuple
from abc import ABC, abstractmethod
from utils.math_utils import Vector2D
from core.player import Player
from render.minimap import Minimap
from utils.logger import get_logger


class IRenderer(ABC):
    """Interface para renderizadores"""

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def render_frame(self, polygons: List[List[Vector2D]], player: Player) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass


class Renderer(IRenderer):
    """Renderizador principal usando Pygame"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen = None
        self.clock = None
        self.minimap = None
        self.logger = get_logger()

    def initialize(self) -> bool:
        """Inicializar el sistema de renderizado"""
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Xoom - Doom-like Engine")
            self.clock = pygame.time.Clock()

            # Inicializar minimapa
            from settings import MINIMAP_SCALE, MINIMAP_POSITION

            self.minimap = Minimap(MINIMAP_SCALE, MINIMAP_POSITION)

            self.logger.info(f"Renderer inicializado: {self.width}x{self.height}")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando renderer: {str(e)}")
            return False

    def render_frame(self, polygons: List[List[Vector2D]], player: Player) -> None:
        """Renderizar un frame completo"""
        from settings import BLACK, PLAYER_FOV

        # Limpiar pantalla
        self.screen.fill(BLACK)

        # Renderizar minimapa
        if self.minimap:
            self.minimap.render(self.screen, polygons, player, PLAYER_FOV)

        # Actualizar pantalla
        pygame.display.flip()

    def get_fps(self) -> float:
        """Obtener los FPS actuales"""
        return self.clock.get_fps()

    def tick(self, fps: int) -> float:
        """Limitar FPS y retornar delta time en segundos"""
        return self.clock.tick(fps) / 1000.0

    def shutdown(self) -> None:
        """Cerrar el sistema de renderizado"""
        pygame.quit()
        self.logger.info("Renderer cerrado")
