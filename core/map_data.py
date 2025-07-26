"""
Estructuras de datos para contener la información del mapa.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from ._types import Segment, Vec2


@dataclass
class MapData:
    """Contiene los segmentos, polígonos y otros datos del mapa."""

    segments: List[Segment] = field(default_factory=list)
    # Almacenará los polígonos por su nombre. Ej: {'world0': [Vec2(..), ...]}
    polygons: Dict[str, List[Vec2]] = field(default_factory=dict)
    # Nuevo: Mapea nombre de polígono a textura de suelo
    polygon_floor_textures: Dict[str, str] = field(default_factory=dict)
    polygon_ceil_textures: Dict[str, str] = field(default_factory=dict)  # <--- NUEVO
    player_start: Vec2 = field(default_factory=lambda: Vec2(0, 0))
    bsp_root: "BSPNode" = None  # noqa: F821 - Forward reference
    # Nuevo: altura de suelo por sector
    sector_floor_h: Dict[str, float] = field(default_factory=dict)
    sector_ceil_h: Dict[str, float] = field(default_factory=dict)  # <--- NUEVO

    def add_segment(self, seg: Segment) -> None:
        self.segments.append(seg)

    def extend(self, segs):
        self.segments.extend(segs)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        if not self.segments:
            return (0, 0, 0, 0)
        xs = []
        ys = []
        for s in self.segments:
            xs.append(s.a.x)
            xs.append(s.b.x)
            ys.append(s.a.y)
            ys.append(s.b.y)
        return min(xs), min(ys), max(xs), max(ys)

    def set_bsp_root(self, bsp_root):
        """
        Asocia el BSPNode raíz y asegura la referencia cruzada a este MapData.
        Esto es necesario para que la lógica de visibilidad funcione correctamente
        cuando se le pasa el BSP en vez del MapData.
        """
        self.bsp_root = bsp_root
        if bsp_root is not None:
            setattr(bsp_root, "map_data", self)
