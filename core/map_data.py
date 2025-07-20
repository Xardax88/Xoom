"""
Estructuras de datos para contener la información del mapa.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from .types import Segment


@dataclass
class MapData:
    """Contiene los segmentos del mapa y sus límites."""
    segments: List[Segment] = field(default_factory=list)

    def add_segment(self, seg: Segment) -> None:
        self.segments.append(seg)

    def extend(self, segs):
        self.segments.extend(segs)

    @property
    def bounds(self):
        if not self.segments:
            return (0, 0, 0, 0)
        xs = []
        ys = []
        for s in self.segments:
            xs.append(s.a.x); xs.append(s.b.x)
            ys.append(s.a.y); ys.append(s.b.y)
        return (min(xs), min(ys), max(xs), max(ys))