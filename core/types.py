"""Tipos básicos y utilitarios para Xoom."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


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


@dataclass(frozen=True)
class Segment:
    a: Vec2
    b: Vec2
    # opcionalmente metadatos: interior/exterior, sector id, etc.
    interior_facing: bool | None = None  # True si normal apunta al interior

    def as_tuple(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return (self.a.as_tuple(), self.b.as_tuple())