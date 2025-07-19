#########################################################################
# utils/math_utils.py - Utilidades matemáticas
#########################################################################

import math
from typing import Tuple

Vector2D = Tuple[float, float]


class MathUtils:
    """Utilidades matemáticas para el juego"""

    @staticmethod
    def distance(p1: Vector2D, p2: Vector2D) -> float:
        """Calcular distancia euclidiana entre dos puntos"""
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """Normalizar ángulo entre 0 y 360 grados"""
        return angle % 360.0

    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convertir grados a radianes"""
        return math.radians(degrees)

    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """Convertir radianes a grados"""
        return math.degrees(radians)

    @staticmethod
    def is_clockwise(vertices: list[Vector2D]) -> bool:
        """Determinar si los vértices están en sentido horario"""
        if len(vertices) < 3:
            return False

        # Calcular el área usando la fórmula del shoelace
        area = 0.0
        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)
            area += (vertices[j][0] - vertices[i][0]) * (
                vertices[j][1] + vertices[i][1]
            )

        return area > 0  # Positivo = horario, Negativo = anti-horario
