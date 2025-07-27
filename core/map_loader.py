# En: core/map_loader.py

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict
import logging

from ._types import Vec2, Segment
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
        """
        Carga un mapa desde un archivo de texto .xmap.
        """
        if not path.exists():
            raise MapLoadError(f"No se encuentra el archivo de mapa: {path}")
        logger.info("Cargando mapa desde %s", path)

        segments: List[Segment] = []
        polygons: Dict[str, List[Vec2]] = {}
        polygon_floor_textures: Dict[str, str] = {}
        sector_floor_h: Dict[str, float] = {}
        sector_ceil_h: Dict[str, float] = {}
        player_start_position: Optional[Vec2] = None
        player_start_angle: float = 0.0  # Ángulo inicial por defecto

        try:
            with path.open("r", encoding="utf-8") as f:
                lines = [
                    ln.strip()
                    for ln in f
                    if ln.strip() and not ln.strip().startswith("#")
                ]
        except Exception as exc:  # noqa: BLE001
            raise MapLoadError(str(exc)) from exc

        i = 0
        sector_count = 0
        sector_vertices = {}
        sector_wall_tex = {}
        sector_floor_tex = {}
        sector_ceil_tex = {}

        while i < len(lines):
            parts = lines[i].split()

            # --- PLAYER_START ---
            if parts[0].upper() == "PLAYER_START":
                if len(parts) < 3:
                    raise MapLoadError(f"Línea PLAYER_START inválida")
                if player_start_position is not None:
                    logger.warning(
                        "Multiples PLAYER_START en el mapa, se usara la primera."
                    )
                try:
                    px, py = map(float, parts[1:3])
                    player_start_position = Vec2(px, py)
                    # Permitir ángulo opcional: PLAYER_START x y [angle]
                    if len(parts) >= 4:
                        player_start_angle = float(parts[3])
                except ValueError as e:
                    raise MapLoadError(
                        f"Coordenadas de PLAYER_START inválidas: {parts[0]}"
                    ) from e
                i += 1
                continue

            # --- SECTOR ---
            if parts[0].upper() == "SECTOR":
                # Formato: SECTOR <floor_h> <ceil_h>
                if len(parts) < 3:
                    raise MapLoadError(f"Línea SECTOR inválida: {lines[i]}")
                try:
                    floor_h = float(parts[1])
                    ceil_h = float(parts[2])
                except Exception as e:
                    raise MapLoadError(
                        f"Valores numéricos inválidos en SECTOR: {lines[i]}"
                    ) from e

                wall_texture = None
                floor_texture = None
                ceil_texture = None
                verts = []
                i += 1

                # Buscar TEXTURES y vértices
                while i < len(lines) and lines[i].upper() != "END":
                    line = lines[i]
                    if line.upper().startswith("TEXTURES"):
                        tex_parts = line.split()
                        wall_texture = tex_parts[1] if len(tex_parts) > 1 else None
                        floor_texture = tex_parts[2] if len(tex_parts) > 2 else None
                        ceil_texture = tex_parts[3] if len(tex_parts) > 3 else None
                    else:
                        # Coordenadas de vértice: x y
                        vparts = line.replace(",", " ").split()
                        if len(vparts) < 2:
                            raise MapLoadError(
                                f"Línea de vértice inválida en SECTOR: {line}"
                            )
                        try:
                            x = float(vparts[0])
                            y = float(vparts[1])
                        except Exception as e:
                            raise MapLoadError(
                                f"Coordenadas de vértice inválidas en SECTOR: {line}"
                            ) from e
                        verts.append(Vec2(x, y))
                    i += 1
                if i == len(lines):
                    raise MapLoadError(f"SECTOR sin END")

                # Guardar polígono y texturas
                sector_name = f"sector_{sector_count}"
                sector_count += 1
                if len(verts) >= 3:
                    polygons[sector_name] = verts
                    polygon_floor_textures[sector_name] = floor_texture or wall_texture
                    # NUEVO: guardar textura de techo y altura de techo
                    if ceil_texture:
                        if "polygon_ceil_textures" not in locals():
                            polygon_ceil_textures = {}
                        polygon_ceil_textures[sector_name] = ceil_texture
                    sector_vertices[sector_name] = verts
                    sector_floor_h[sector_name] = floor_h
                    sector_ceil_h[sector_name] = ceil_h
                    sector_wall_tex[sector_name] = wall_texture
                    sector_floor_tex[sector_name] = floor_texture
                    sector_ceil_tex[sector_name] = ceil_texture
                i += 1  # Saltar END
                continue

            raise MapLoadError(f"Token desconocido: {parts[0]}")

        # --- Generación de segmentos exteriores y paredes entre sectores ---
        # Creamos un índice de bordes: (v1, v2) -> [(sector, idx)]
        edge_index: Dict[tuple, list] = {}
        for sector, verts in sector_vertices.items():
            n = len(verts)
            for idx in range(n):
                v1 = verts[idx]
                v2 = verts[(idx + 1) % n]
                key = tuple(sorted([(v1.x, v1.y), (v2.x, v2.y)]))
                edge_index.setdefault(key, []).append((sector, idx))

        # Limpiamos la lista de segmentos para solo agregar los correctos
        segments = []

        for key, refs in edge_index.items():
            if len(refs) == 1:
                # --- Pared exterior: solo un sector tiene este borde ---
                sector, idx = refs[0]
                verts = sector_vertices[sector]
                n = len(verts)
                v1 = verts[idx]
                v2 = verts[(idx + 1) % n]
                wall_tex = sector_wall_tex[sector]
                floor_h = sector_floor_h[sector]
                ceil_h = sector_ceil_h[sector]
                # Siempre exterior: interior_facing=False y sentido antihorario (v1 -> v2)
                segment = Segment(
                    a=v1,
                    b=v2,
                    interior_facing=False,  # Exterior: normal hacia fuera del sector
                    texture_name=wall_tex,
                    height=ceil_h - floor_h,
                    polygon_name=sector,
                    portal_h1_a=floor_h,
                    portal_h1_b=floor_h,
                    portal_h2_a=ceil_h,
                    portal_h2_b=ceil_h,
                    wall_type="solid",
                )
                segments.append(segment)
            elif len(refs) == 2:
                # --- Borde compartido entre dos sectores ---
                (sectorA, idxA), (sectorB, idxB) = refs
                vertsA = sector_vertices[sectorA]
                vertsB = sector_vertices[sectorB]
                nA = len(vertsA)
                nB = len(vertsB)
                vA1 = vertsA[idxA]
                vA2 = vertsA[(idxA + 1) % nA]
                vB1 = vertsB[idxB]
                vB2 = vertsB[(idxB + 1) % nB]
                # Emparejar extremos por cercanía
                if (
                    abs(vA1.x - vB2.x) < 1e-4
                    and abs(vA1.y - vB2.y) < 1e-4
                    and abs(vA2.x - vB1.x) < 1e-4
                    and abs(vA2.y - vB1.y) < 1e-4
                ):
                    vB1, vB2 = vB2, vB1

                # Alturas de suelo y techo en cada sector
                floorA = sector_floor_h[sectorA]
                ceilA = sector_ceil_h[sectorA]
                floorB = sector_floor_h[sectorB]
                ceilB = sector_ceil_h[sectorB]

                # Si ambos sectores tienen el mismo floor_h y ceil_h, NO hay pared entre ellos
                if abs(floorA - floorB) < 1e-4 and abs(ceilA - ceilB) < 1e-4:
                    continue  # No se genera pared

                # Si floor_h o ceil_h es distinto, crear pared tipo portal
                if not abs(floorA - floorB) < 1e-4 or not abs(ceilA - ceilB) < 1e-4:
                    # Determinar los valores extremos para dividir la pared en 3 secciones
                    min_floor = min(floorA, floorB)
                    max_floor = max(floorA, floorB)
                    min_ceil = min(ceilA, ceilB)
                    max_ceil = max(ceilA, ceilB)
                    if min_ceil <= min_floor:
                        continue  # No hay espacio para pared

                    wall_tex = sector_wall_tex[sectorA] or sector_wall_tex[sectorB]
                    # Dividir la pared en 3 secciones: superior, central, inferior
                    # Sección superior: de min_ceil a max_ceil (si hay diferencia)
                    # Sección central: de max_floor a min_ceil (zona de paso)
                    # Sección inferior: de min_floor a max_floor (si hay diferencia)
                    portal_sections = []
                    # Superior
                    if abs(max_ceil - min_ceil) > 1e-4:
                        portal_sections.append(
                            {
                                "section": "top",
                                "h1_a": min_ceil,
                                "h1_b": min_ceil,
                                "h2_a": max_ceil,
                                "h2_b": max_ceil,
                            }
                        )
                    # Central (zona de paso)
                    portal_sections.append(
                        {
                            "section": "middle",
                            "h1_a": max_floor,
                            "h1_b": max_floor,
                            "h2_a": min_ceil,
                            "h2_b": min_ceil,
                        }
                    )
                    # Inferior
                    if abs(max_floor - min_floor) > 1e-4:
                        portal_sections.append(
                            {
                                "section": "bottom",
                                "h1_a": min_floor,
                                "h1_b": min_floor,
                                "h2_a": max_floor,
                                "h2_b": max_floor,
                            }
                        )

                    # El segmento se dibuja en la posición del borde compartido
                    portal_segment = Segment(
                        a=vA1,
                        b=vA2,
                        interior_facing=False,
                        texture_name=wall_tex,
                        height=max_ceil - min_floor,
                        polygon_name=f"{sectorA}_to_{sectorB}_portal",
                        portal_h1_a=min_floor,
                        portal_h1_b=min_floor,
                        portal_h2_a=max_ceil,
                        portal_h2_b=max_ceil,
                        wall_type="portal",
                        portal_sections=portal_sections,
                        blocks_collision=False,  # <--- Permite el paso y visibilidad en portales
                    )
                    segments.append(portal_segment)

        # Crear MapData con los segmentos correctos
        md = MapData(
            segments=segments,
            polygons=polygons,
            polygon_floor_textures=polygon_floor_textures,
            polygon_ceil_textures=locals().get("polygon_ceil_textures", {}),
        )
        md.sector_floor_h = sector_floor_h
        md.sector_ceil_h = sector_ceil_h

        if player_start_position:
            md.player_start = player_start_position
            logger.info("Posición del jugador: %s", player_start_position)
        else:
            logger.info(
                "No se encontró la posición del jugador en el mapa. Se usará la posición (0, 0)."
            )

        # --- Guardar el ángulo inicial del jugador en el MapData ---
        md.player_start_angle = player_start_angle

        self._preload_textures(md.segments)

        logger.info(
            "Mapa: %s segmentos y %s polígonos cargados.",
            len(md.segments),
            len(md.polygons),
        )
        return md

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
