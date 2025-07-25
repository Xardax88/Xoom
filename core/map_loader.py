# En: core/map_loader.py

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict
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
    def __init__(self, texture_manager=None):
        self.texture_manager = texture_manager

    def load(self, path: Path) -> MapData:
        if not path.exists():
            raise MapLoadError(f"No se encuentra el archivo de mapa: {path}")
        logger.info("Cargando mapa desde %s", path)

        segments: List[Segment] = []
        polygons: Dict[str, List[Vec2]] = {}
        polygon_floor_textures: Dict[str, str] = {}
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

            # --- Nuevo formato de POLY y SEG ---
            if parts[0].upper() in ("POLY", "SEG"):
                tipo = parts[0].upper()
                name = parts[1] if len(parts) > 1 else f"{tipo.lower()}_{len(polygons)}"
                # Nuevo formato: <TIPO> <nombre> <altura> <textura_pared> <textura_suelo(opcional)> <textura_techo(opcional)>
                try:
                    height = float(parts[2]) if len(parts) > 2 else None
                except ValueError:
                    raise MapLoadError(f"Altura inválida para {tipo} {name}")

                texture_wall = parts[3] if len(parts) > 3 else None
                # Si no hay textura de suelo, usar la de pared
                texture_floor = parts[4] if len(parts) > 4 else texture_wall
                # Si no hay textura de techo, usar la de pared
                texture_ceil = parts[5] if len(parts) > 5 else texture_wall

                # Leer vértices hasta END
                verts = []
                i += 1
                while i < len(lines) and lines[i].upper() != "END":
                    vparts = lines[i].replace(",", " ").split()
                    if len(vparts) < 2:
                        raise MapLoadError(f"Línea de vértice inválida en {tipo} {name}: {lines[i]}")
                    try:
                        x = float(vparts[0])
                        y = float(vparts[1])
                        # t y b por ahora no se usan, pero se leen para el futuro
                        t = float(vparts[2]) if len(vparts) > 2 else 0.0
                        b = float(vparts[3]) if len(vparts) > 3 else 0.0
                    except Exception as e:
                        raise MapLoadError(f"Coordenadas de vértice inválidas en {tipo} {name}: {lines[i]}") from e
                    verts.append(Vec2(x, y))
                    i += 1
                if i == len(lines):
                    raise MapLoadError(f"{tipo} {name} sin END")

                if tipo == "POLY":
                    # Guardar los vértices del polígono
                    if len(verts) >= 3:
                        polygons[name] = verts
                        # Guardar la textura de suelo asociada al polígono
                        polygon_floor_textures[name] = texture_floor
                        # Determinar orientación para interior_facing según convención:
                        # - Horario: interior_facing=True (columnas, pilares)
                        # - Antihorario: interior_facing=False (habitaciones, áreas transitables)
                        from utils.math_utils import is_clockwise
                        is_interior = is_clockwise(verts)
                        # CORRECCIÓN: invertir para habitaciones (antihorario)
                        poly_segments = self._create_segments_from_poly(
                            vertices=verts,
                            polygon_name=name,
                            interior_facing=is_interior,
                            texture_name=texture_wall,
                            height=height,
                        )
                        segments.extend(poly_segments)
                elif tipo == "SEG":
                    # Un segmento es solo dos puntos
                    if len(verts) == 2:
                        seg = Segment(
                            a=verts[0],
                            b=verts[1],
                            interior_facing=True,  # Por defecto
                            texture_name=texture_wall,
                            height=height,
                            polygon_name= name,
                        )
                        segments.append(seg)
                i += 1  # Saltar END
                continue

            raise MapLoadError(f"Token desconocido: {parts[0]}")

        # Crear MapData con segmentos, polígonos y texturas de suelo
        md = MapData(segments=segments, polygons=polygons, polygon_floor_textures=polygon_floor_textures)

        if player_start_position:
            md.player_start = player_start_position
            logger.info("Posición del jugador: %s", player_start_position)
        else:
            logger.info("No se encontró la posición del jugador en el mapa. Se usará la posición (0, 0).")

        self._preload_textures(md.segments)

        logger.info("Mapa: %s segmentos y %s polígonos cargados.", len(md.segments), len(md.polygons))
        return md

    def _create_segments_from_poly(
            self,
            vertices: list[Vec2],
            polygon_name: str,
            interior_facing: bool,
            texture_name: Optional[str] = None,
            height: Optional[float] = None,
    ) -> list[Segment]:
        """
        Crea segmentos a partir de una lista de vértices, etiquetándolos
        con el nombre de su polígono padre.
        Para cumplir la convención:
        - Polígonos en sentido horario (columnas): segmentos CCW, interior_facing=True.
        - Polígonos en sentido antihorario (habitaciones): segmentos CW, interior_facing=False.
        """
        segments = []
        if len(vertices) < 2:
            return segments

        cumulative_length = 0.0

        n = len(vertices)
        for i in range(n):
            if interior_facing:
                # Columnas: sentido horario, segmento de i a (i+1)
                p1 = vertices[i]
                p2 = vertices[(i + 1) % n]
                facing = True
            else:
                # Habitaciones: sentido antihorario, segmento de (i+1) a i (invertido)
                p1 = vertices[(i + 1) % n]
                p2 = vertices[i]
                facing = False

            segment = Segment(
                a=p1,
                b=p2,
                u_offset=cumulative_length,
                interior_facing=facing,
                texture_name=texture_name,
                height=height,
                polygon_name=polygon_name,
            )
            cumulative_length += segment.length()
            segments.append(segment)

        return segments

    def _preload_textures(self, segments: List[Segment]) -> None:
        """
        Precarga todas las texturas únicas utilizadas en los segmentos.
        """
        if not self.texture_manager:
            return

        unique_textures = {seg.texture_name for seg in segments if seg.texture_name}
        for texture_name in unique_textures:
            try:
                self.texture_manager.get_gl_texture_id(texture_name)
                logger.debug(f"Textura precargada: {texture_name}")
            except FileNotFoundError:
                logger.warning(f"No se pudo cargar la textura: {texture_name}")
