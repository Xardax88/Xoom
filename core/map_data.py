"""
Estructuras de datos para contener la información del mapa.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from ._types import Segment, Vec2


@dataclass
class MapData:
    """
    Contiene los segmentos, polígonos y otros datos del mapa.
    Puede inicializarse directamente con los campos o usando el método de clase from_xmap.
    """

    segments: List[Segment] = field(default_factory=list)
    # Almacenará los polígonos por su nombre. Ej: {'world0': [Vec2(..), ...]}
    polygons: Dict[str, List[Vec2]] = field(default_factory=dict)
    # Nuevo: Mapea nombre de polígono a textura de suelo
    polygon_floor_textures: Dict[str, str] = field(default_factory=dict)
    polygon_ceil_textures: Dict[str, str] = field(default_factory=dict)  # <--- NUEVO
    player_start: Vec2 = field(default_factory=lambda: Vec2(0, 0))
    player_start_angle: float = 0.0  # Ángulo inicial del jugador en grados
    bsp_root: Optional["BSPNode"] = None  # noqa: F821 - Forward reference
    # Nuevo: altura de suelo por sector
    sector_floor_h: Dict[str, float] = field(default_factory=dict)
    sector_ceil_h: Dict[str, float] = field(default_factory=dict)  # <--- NUEVO

    @classmethod
    def from_xmap(cls, xmap_data: dict) -> "MapData":
        """
        Crea una instancia de MapData a partir de un diccionario xmap_data.
        Extrae los campos relevantes y los asigna correctamente.
        """
        # Extraer posición y ángulo inicial del jugador
        player_start_tuple = xmap_data.get("player_start_pos", (0.0, 0.0))
        player_start = Vec2(*player_start_tuple)
        player_start_angle = xmap_data.get("player_start_angle", 0.0)

        # Extraer otros campos si existen, o usar valores por defecto
        return cls(
            segments=xmap_data.get("segments", []),
            polygons=xmap_data.get("polygons", {}),
            polygon_floor_textures=xmap_data.get("polygon_floor_textures", {}),
            polygon_ceil_textures=xmap_data.get("polygon_ceil_textures", {}),
            player_start=player_start,
            player_start_angle=player_start_angle,
            sector_floor_h=xmap_data.get("sector_floor_h", {}),
            sector_ceil_h=xmap_data.get("sector_ceil_h", {}),
        )

    def add_segment(self, seg: Segment) -> None:
        """Agrega un segmento a la lista de segmentos del mapa."""
        self.segments.append(seg)

    def extend(self, segs):
        """Agrega múltiples segmentos a la lista de segmentos del mapa."""
        self.segments.extend(segs)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """Calcula los límites (bounding box) del mapa."""
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
