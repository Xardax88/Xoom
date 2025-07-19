#########################################################################
# render/minimap.py - Renderizador del minimapa
#########################################################################

import pygame
from typing import List, Tuple
from utils.math_utils import Vector2D
from core.player import Player
from utils.logger import get_logger


class Minimap:
    """Renderizador del minimapa siguiendo el principio de Responsabilidad Única"""

    def __init__(self, scale: float, position: Tuple[int, int]):
        self.scale = scale
        self.position = position
        self.logger = get_logger()

    def render(
        self,
        surface: pygame.Surface,
        polygons: List[List[Vector2D]],
        player: Player,
        fov_angle: float,
    ) -> None:
        """Renderizar el minimapa en la superficie dada"""
        from settings import WHITE, RED, YELLOW, PLAYER_SIZE

        # Renderizar polígonos del mapa
        for polygon in polygons:
            if len(polygon) >= 3:
                scaled_points = [
                    (
                        self.position[0] + int(point[0] * self.scale),
                        self.position[1] + int(point[1] * self.scale),
                    )
                    for point in polygon
                ]
                pygame.draw.polygon(surface, WHITE, scaled_points, 1)

        # Renderizar jugador
        player_screen_pos = (
            self.position[0] + int(player.x * self.scale),
            self.position[1] + int(player.y * self.scale),
        )

        pygame.draw.circle(
            surface, RED, player_screen_pos, max(1, int(PLAYER_SIZE * self.scale))
        )

        # Renderizar líneas de FOV
        fov_lines = player.get_fov_lines(fov_angle, 100)

        # Línea izquierda del FOV
        left_end_screen = (
            self.position[0] + int(fov_lines[0][0] * self.scale),
            self.position[1] + int(fov_lines[0][1] * self.scale),
        )
        pygame.draw.line(surface, YELLOW, player_screen_pos, left_end_screen, 1)

        # Línea derecha del FOV
        right_end_screen = (
            self.position[0] + int(fov_lines[1][0] * self.scale),
            self.position[1] + int(fov_lines[1][1] * self.scale),
        )
        pygame.draw.line(surface, YELLOW, player_screen_pos, right_end_screen, 1)
