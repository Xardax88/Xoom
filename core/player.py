#########################################################################
# core/player.py - Clase que representa al jugador
#########################################################################

import math
from typing import Tuple
from utils.math_utils import Vector2D, MathUtils


class Player:
    """Representa al jugador en el juego siguiendo el principio de Responsabilidad Única"""

    def __init__(self, x: float, y: float, angle: float = 0.0):
        self.x = x
        self.y = y
        self.angle = angle  # en grados
        self.speed = 0.0
        self.rotation_speed = 0.0

    @property
    def position(self) -> Vector2D:
        """Obtener la posición actual del jugador"""
        return (self.x, self.y)

    @property
    def direction_vector(self) -> Vector2D:
        """Obtener el vector de dirección basado en el ángulo actual"""
        rad = MathUtils.degrees_to_radians(self.angle)
        return (math.cos(rad), math.sin(rad))

    def update(self, delta_time: float) -> None:
        """Actualizar la posición del jugador"""
        if self.speed != 0:
            direction = self.direction_vector
            self.x += direction[0] * self.speed * delta_time
            self.y += direction[1] * self.speed * delta_time

        if self.rotation_speed != 0:
            self.angle += self.rotation_speed * delta_time
            self.angle = MathUtils.normalize_angle(self.angle)

    def set_movement(self, speed: float) -> None:
        """Establecer la velocidad de movimiento"""
        self.speed = speed

    def set_rotation(self, rotation_speed: float) -> None:
        """Establecer la velocidad de rotación"""
        self.rotation_speed = rotation_speed

    def get_fov_lines(
        self, fov_angle: float, length: float = 100
    ) -> Tuple[Vector2D, Vector2D]:
        """Obtener las líneas que representan el campo de visión"""
        half_fov = fov_angle / 2

        # Línea izquierda del FOV
        left_angle = MathUtils.degrees_to_radians(self.angle - half_fov)
        left_end = (
            self.x + math.cos(left_angle) * length,
            self.y + math.sin(left_angle) * length,
        )

        # Línea derecha del FOV
        right_angle = MathUtils.degrees_to_radians(self.angle + half_fov)
        right_end = (
            self.x + math.cos(right_angle) * length,
            self.y + math.sin(right_angle) * length,
        )

        return (left_end, right_end)
