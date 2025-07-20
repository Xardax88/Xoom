"""
Carga de archivos de mapa (.xmap).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
import logging

from .types import Vec2, Segment
from .math_utils import is_clockwise
from .map_data import MapData
from .errors import MapLoadError

logger = logging.getLogger(__name__)


class IMapLoader(ABC):
    """Interfaz para cargadores de mapas."""
    @abstractmethod
    def load(self, path: Path) -> MapData:  # pragma: no cover - interface
        ...


class FileMapLoader(IMapLoader):
    """Implementación que lee un archivo de texto .xmap."""

    def load(self, path: Path) -> MapData:
        if not path.exists():
            raise MapLoadError(f"No se encuentra el archivo de mapa: {path}")
        logger.info("Cargando mapa desde %s", path)

        segments: List[Segment] = []
        try:
            with path.open("r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith('#')]
        except Exception as exc:  # noqa: BLE001
            raise MapLoadError(str(exc)) from exc

        i = 0
        while i < len(lines):
            parts = lines[i].split()
            if parts[0].upper() == "SEG":
                if len(parts) != 5:
                    raise MapLoadError(f"Línea SEG inválida: {lines[i]}")
                x1, y1, x2, y2 = map(float, parts[1:])
                segments.append(Segment(Vec2(x1, y1), Vec2(x2, y2)))
                i += 1
                continue

            if parts[0].upper() == "POLY":
                name = parts[1] if len(parts) > 1 else "poly"
                pts: List[Vec2] = []
                i += 1
                while i < len(lines) and lines[i].upper() != "END":
                    xy = lines[i].split()
                    if len(xy) != 2:
                        raise MapLoadError(f"Línea de punto inválida en polígono {name}: {lines[i]}")
                    pts.append(Vec2(float(xy[0]), float(xy[1])))
                    i += 1
                if i == len(lines):
                    raise MapLoadError(f"Polígono {name} sin END")
                # cerrar polígono
                if len(pts) >= 2:
                    # orientación
                    cw = is_clockwise(pts)
                    for j in range(len(pts)):
                        a = pts[j]
                        b = pts[(j + 1) % len(pts)]
                        seg = Segment(a, b, interior_facing=cw)
                        segments.append(seg)
                i += 1  # saltar END
                continue

            raise MapLoadError(f"Token desconocido: {parts[0]}")

        md = MapData(segments=segments)
        logger.info("Mapa: %s segmentos cargados.", len(md.segments))
        return md