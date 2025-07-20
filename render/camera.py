"""
Cámara 2D para convertir coordenadas de mundo a pantalla (minimap).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass
class MiniMapCamera:
    width: int
    height: int
    scale: float
    margin: int

    def world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        # origen del mundo (0,0) centrado?
        # Aquí elegimos desplazar el mundo al centro de la ventana.
        sx = int(self.width / 2 + x * self.scale)
        sy = int(self.height / 2 - y * self.scale)  # eje Y invertido para pantalla
        return sx, sy
