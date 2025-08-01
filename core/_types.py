"""
Tipos básicos y utilitarios para el Engine.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, replace as dataclass_replace, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class Vec2:
    x: float
    y: float

    def as_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, k: float) -> "Vec2":
        return Vec2(self.x * k, self.y * k)

    __rmul__ = __mul__

    def length(self) -> float:
        dx = self.x - 0.0
        dy = self.y - 0.0
        return math.sqrt(dx * dx + dy * dy)


@dataclass(frozen=True)
class Segment:
    """
    Representa un segmento de pared o límite en el mapa.
    El atributo blocks_collision indica si este segmento bloquea el movimiento (colisión).
    Si blocks_collision es False, el segmento es solo visual (no bloquea ni colisión ni visibilidad).

    wall_type: Indica si la pared es 'solid' (normal) o 'portal' (dividida en secciones).
    portal_sections: Solo para wall_type='portal'. Lista de dicts con info de cada sección.
    NOTA: portal_sections se excluye de hash y comparación para permitir que Segment sea hashable.
    """

    a: Vec2
    b: Vec2
    # opcionalmente metadatos: interior/exterior, sector id, etc.
    interior_facing: bool | None = None  # True si normal apunta al interior
    u_offset: float = 0.0
    texture_name: str | None = None
    height: float | None = None
    original_segment: Optional["Segment"] = field(
        default=None, compare=False, hash=False
    )
    polygon_name: Optional[str] = None
    # --- NUEVO: atributos para soporte de portales ---
    portal_section: str = None  # "top", "bottom" o None
    portal_h1_a: float = 0.0
    portal_h1_b: float = 0.0
    portal_h2_a: float = 0.0
    portal_h2_b: float = 0.0
    blocks_collision: bool = True  # <--- Añadido para control de colisión

    # --- NUEVO: tipo de pared y secciones de portal ---
    wall_type: str = "solid"  # 'solid' (normal) o 'portal'
    # Excluir portal_sections de hash y comparación para evitar errores con listas mutables
    portal_sections: Optional[list] = field(
        default=None, compare=False, hash=False, repr=False
    )

    def __post_init__(self):
        """
        Si no se proporciona un segmento original asigna uno.
        Si es pared portal y no se definen secciones, inicializa como lista vacía.
        """
        if self.original_segment is None:
            object.__setattr__(self, "original_segment", self)
        if self.wall_type == "portal" and self.portal_sections is None:
            object.__setattr__(self, "portal_sections", [])

    def length(self) -> float:
        dx = self.b.x - self.a.x
        dy = self.b.y - self.a.y
        return math.sqrt(dx * dx + dy * dy)

    def as_tuple(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return (self.a.as_tuple(), self.b.as_tuple())

    def replace(self, **change) -> "Segment":
        """
        Crea una instalcia del segmento
        """
        return dataclass_replace(self, **change)
