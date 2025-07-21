from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import logging

from .types import Vec2, Segment
from utils.math_utils import is_clockwise
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
        player_start_position: Optional[Vec2] = None

        try:
            with path.open("r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith('#')]
        except Exception as exc:  # noqa: BLE001
            raise MapLoadError(str(exc)) from exc

        i = 0
        while i < len(lines):
            parts = lines[i].split()

            if parts[0].upper() == "PLAYER_START":
                if len(parts) != 3:
                    raise MapLoadError(f"Línea PLAYER_START inválida")
                if player_start_position is not None:
                    logger.warning("Multiples PLAYER_START en el mapa, se usara la primera.")
                try:
                    px, py = map(float, parts[1:])
                    player_start_position = Vec2(px, py)
                except ValueError as e:
                    raise MapLoadError(f"Coordenadas de PLAYER_START inválidas: {parts[0]}") from e
                i += 1
                continue

            if parts[0].upper() == "SEG":
                if len(parts) != 5:
                    raise MapLoadError(f"Línea SEG inválida: {lines[i]}")
                x1, y1, x2, y2 = map(float, parts[1:])
                segments.append(Segment(Vec2(x1, y1), Vec2(x2, y2)))
                i += 1
                continue

            if parts[0].upper() == "POLY":
                # POLY <name> [texture] [height]
                name = parts[1] if len(parts) > 1 else "poly"
                texture_name = parts[2] if len(parts) > 2 else None
                try:
                    height = float(parts[3]) if len(parts) > 3 else None
                except ValueError:
                    raise MapLoadError(f"Altura inválida para el polígono {name}")

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

                if len(pts) >= 2:
                    is_interior = is_clockwise(pts)
                    poly_segments = self._create_segments_from_poly(
                        vertices=pts,
                        interior_facing=is_interior,
                        texture_name=texture_name,
                        height=height,
                    )
                    segments.extend(poly_segments)

                i += 1  # saltar END
                continue

            raise MapLoadError(f"Token desconocido: {parts[0]}")

        md = MapData(segments=segments)

        if player_start_position:
            md.player_start = player_start_position
            logger.info("Posición del jugador: %s", player_start_position)
        else:
            logger.info("No se encontró la posición del jugador en el mapa. Se usará la posición (0, 0).")

        logger.info("Mapa: %s segmentos cargados.", len(md.segments))
        return md

    def _create_segments_from_poly(
        self,
        vertices: list[Vec2],
        interior_facing: bool,
        texture_name: Optional[str] = None,
        height: Optional[float] = None,
    ) -> list[Segment]:
        """
        Crea segmentos a partir de una lista de vértices, calculando el
        desfase de textura acumulativo (u_offset) y asignando la orientación.
        """
        segments = []
        if len(vertices) < 2:
            return segments

        cumulative_length = 0.0

        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]

            # Creamos el segmento con todos sus datos, incluido el u_offset
            segment = Segment(
                a=p1,
                b=p2,
                u_offset=cumulative_length,
                interior_facing=interior_facing,
                texture_name=texture_name,
                height=height,
            )
            segments.append(segment)

            # Acumulamos la longitud para el siguiente segmento
            cumulative_length += segment.length()

        return segments