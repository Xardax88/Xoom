"""
Definición del jugador.
"""

from __future__ import annotations
from dataclasses import dataclass
import math
from ._types import Vec2


@dataclass
class Player:
    x: float
    y: float
    angle_deg: float
    fov_deg: float
    fov_length: float

    @property
    def pos(self) -> Vec2:
        return Vec2(self.x, self.y)

    @property
    def angle_rad(self) -> float:
        """Ángulo actual en radianes (derivado de angle_deg)."""
        return math.radians(self.angle_deg)

    def rotate(self, delta_deg: float) -> None:
        self.angle_deg = (self.angle_deg + delta_deg) % 360.0

    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    def forward_vector(self) -> Vec2:
        rad = math.radians(self.angle_deg)
        return Vec2(math.cos(rad), math.sin(rad))

    def fov_edges(self) -> tuple[Vec2, Vec2]:
        """Devuelve los extremos del FOV como puntos en mundo."""
        half = self.fov_deg / 2.0
        a1 = math.radians(self.angle_deg - half)
        a2 = math.radians(self.angle_deg + half)
        return (
            Vec2(
                self.x + math.cos(a1) * self.fov_length,
                self.y + math.sin(a1) * self.fov_length,
            ),
            Vec2(
                self.x + math.cos(a2) * self.fov_length,
                self.y + math.sin(a2) * self.fov_length,
            ),
        )
