"""
Tipos básicos y utilitarios para Xoom.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, replace as dataclass_replace
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
    a: Vec2
    b: Vec2
    # opcionalmente metadatos: interior/exterior, sector id, etc.
    interior_facing: bool | None = None  # True si normal apunta al interior
    u_offset: float = 0.0
    texture_name: str | None = None
    height: float | None = None
    original_segment: Optional["Segment"] = None
    polygon_name: Optional[str] = None

    def __post_init__(self):
        """
        Si no se proporciona un segmento original asigna uno
        """
        if self.original_segment is None:
            object.__setattr__(self, "original_segment", self)

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