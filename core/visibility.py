"""
VisibilityManager: Lógica de visibilidad basada en FOV para el motor 3D.
Muestra todos los segmentos (caras) de los polígonos principales que entren, aunque sea parcialmente,
dentro del cono del FOV del jugador.
"""

from __future__ import annotations
from typing import List
import math

from ._types import Segment, Vec2
from .map_data import MapData
from .player import Player


class VisibilityManager:
    """
    Gestiona la visibilidad de los segmentos del mapa.
    Un segmento es visible si al menos uno de sus extremos está dentro del FOV del jugador,
    o si el segmento cruza el cono del FOV.
    """

    @staticmethod
    def compute_visible_segments(
        map_or_bsp,
        player: Player,
        max_dist: float | None = None,
        clip_to_fov: bool = None,
        see_through_portals: bool = True,  # Nuevo: permite ver a través de portales
    ) -> List[Segment]:
        """
        Devuelve todos los segmentos (caras) de los polígonos principales que entren parcialmente en el FOV,
        excluyendo aquellos completamente cubiertos por otros más cercanos al jugador.
        El filtrado de oclusión se realiza mediante raycasting desde la posición del jugador.

        Si see_through_portals=True, los segmentos tipo 'portal' no bloquean la visibilidad de otros segmentos detrás.
        """
        # Permite recibir MapData o BSPNode
        if hasattr(map_or_bsp, "segments"):
            map_data = map_or_bsp
        elif hasattr(map_or_bsp, "map_data") and hasattr(
            map_or_bsp.map_data, "segments"
        ):
            map_data = map_or_bsp.map_data
        else:
            raise AttributeError(
                "compute_visible_segments requiere un MapData o un BSPNode con atributo 'map_data' que apunte a MapData."
            )

        if max_dist is None:
            max_dist = player.fov_length

        pos = Vec2(player.x, player.y)
        ang = math.radians(player.angle_deg)
        fov_rad = math.radians(player.fov_deg)
        half_fov = fov_rad / 2
        max_d2 = max_dist * max_dist

        visible_segments = []
        for seg in map_data.segments:
            if (
                VisibilityManager._point_in_fov(seg.a, pos, ang, half_fov, max_d2)
                or VisibilityManager._point_in_fov(seg.b, pos, ang, half_fov, max_d2)
                or VisibilityManager._segment_crosses_fov(
                    seg, pos, ang, half_fov, max_dist
                )
            ):
                visible_segments.append(seg)

        # --- Filtrado de segmentos totalmente cubiertos usando raycasting ---
        filtered_segments = VisibilityManager._filter_occluded_segments_raycast(
            visible_segments, player, max_dist, see_through_portals=see_through_portals
        )
        return filtered_segments

    @staticmethod
    def _filter_occluded_segments_raycast(
        segments: List[Segment],
        player: Player,
        max_dist: float,
        ray_count: int = 256,
        see_through_portals: bool = True,  # Nuevo: permite ver a través de portales
    ) -> List[Segment]:
        """
        Filtra los segmentos que están completamente cubiertos por otros usando raycasting.
        Se lanzan rayos desde la posición del jugador en el rango del FOV.
        Solo los segmentos que son impactados primero por al menos un rayo se consideran visibles.

        Si see_through_portals=True, los segmentos tipo 'portal' no bloquean la visibilidad de otros segmentos detrás,
        pero siguen siendo visibles si están en el FOV.
        """
        if not segments:
            return []

        pos = Vec2(player.x, player.y)
        ang = math.radians(player.angle_deg)
        fov_rad = math.radians(player.fov_deg)
        half_fov = fov_rad / 2

        # Mapa: segmento -> set de índices de rayos que lo impactan primero
        segment_hits = {seg: set() for seg in segments}

        # Lanzar rayos en el FOV
        for i in range(ray_count):
            rel = i / (ray_count - 1) if ray_count > 1 else 0.5
            ray_angle = ang - half_fov + rel * fov_rad
            dx = math.cos(ray_angle)
            dy = math.sin(ray_angle)
            ray_end = Vec2(pos.x + dx * max_dist, pos.y + dy * max_dist)

            # Buscar todos los segmentos impactados por el rayo, ordenados por distancia
            hits = []
            for seg in segments:
                hit = VisibilityManager._segment_ray_intersection(
                    pos, ray_end, seg.a, seg.b
                )
                if hit is not None:
                    dist = (hit.x - pos.x) ** 2 + (hit.y - pos.y) ** 2
                    hits.append((dist, seg))

            hits.sort()
            # Marca todos los portales impactados por este rayo como visibles,
            # y solo el primer sólido impactado (si lo hay)
            for dist, seg in hits:
                segment_hits[seg].add(i)
                if getattr(seg, "wall_type", "solid") != "portal":
                    # Si es sólido, detén el rayo aquí
                    break
                # Si es portal, sigue buscando detrás

        # Solo los segmentos impactados por al menos un rayo son visibles
        visible = [seg for seg, rays in segment_hits.items() if rays]
        return visible

    @staticmethod
    def _segment_ray_intersection(
        ray_a: Vec2, ray_b: Vec2, seg_a: Vec2, seg_b: Vec2
    ) -> Vec2 | None:
        """
        Calcula la intersección entre un rayo (ray_a -> ray_b) y un segmento (seg_a, seg_b).
        Devuelve el punto de intersección si existe y está en el rango del rayo y del segmento.
        """
        # Algoritmo de intersección de segmentos (paramétrico)
        dx1 = ray_b.x - ray_a.x
        dy1 = ray_b.y - ray_a.y
        dx2 = seg_b.x - seg_a.x
        dy2 = seg_b.y - seg_a.y

        denom = dx1 * dy2 - dy1 * dx2
        if abs(denom) < 1e-8:
            return None  # Paralelos

        t = ((seg_a.x - ray_a.x) * dy2 - (seg_a.y - ray_a.y) * dx2) / denom
        u = ((seg_a.x - ray_a.x) * dy1 - (seg_a.y - ray_a.y) * dx1) / denom

        if t < 0 or t > 1:
            return None  # Intersección fuera del rayo
        if u < 0 or u > 1:
            return None  # Intersección fuera del segmento

        ix = ray_a.x + t * dx1
        iy = ray_a.y + t * dy1
        return Vec2(ix, iy)

    @staticmethod
    def _point_in_fov(
        p: Vec2, pos: Vec2, ang: float, half_fov: float, max_d2: float
    ) -> bool:
        """
        Determina si el punto p está dentro del cono del FOV y rango máximo.
        """
        dx = p.x - pos.x
        dy = p.y - pos.y
        d2 = dx * dx + dy * dy
        if d2 > max_d2:
            return False
        pa = math.atan2(dy, dx)
        da = VisibilityManager._angle_diff(pa, ang)
        return abs(da) <= half_fov

    @staticmethod
    def _segment_crosses_fov(
        seg: Segment, pos: Vec2, ang: float, half_fov: float, max_dist: float
    ) -> bool:
        """
        Determina si el segmento cruza el cono del FOV.
        """
        # Definir los dos bordes del FOV como rayos
        fov_left = ang - half_fov
        fov_right = ang + half_fov
        left_dir = Vec2(math.cos(fov_left), math.sin(fov_left))
        right_dir = Vec2(math.cos(fov_right), math.sin(fov_right))
        left_end = Vec2(pos.x + left_dir.x * max_dist, pos.y + left_dir.y * max_dist)
        right_end = Vec2(pos.x + right_dir.x * max_dist, pos.y + right_dir.y * max_dist)

        # Revisar si el segmento cruza alguno de los bordes del FOV
        if VisibilityManager._segments_intersect(
            pos, left_end, seg.a, seg.b
        ) or VisibilityManager._segments_intersect(pos, right_end, seg.a, seg.b):
            return True

        # Revisar si el segmento cruza la base del triángulo FOV
        base_a = left_end
        base_b = right_end
        if VisibilityManager._segments_intersect(base_a, base_b, seg.a, seg.b):
            return True

        return False

    @staticmethod
    def _angle_diff(a: float, b: float) -> float:
        """
        Calcula la diferencia angular normalizada entre dos ángulos en radianes.
        """
        d = a - b
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        return d

    @staticmethod
    def _segments_intersect(a1: Vec2, a2: Vec2, b1: Vec2, b2: Vec2) -> bool:
        """
        Determina si los segmentos a1-a2 y b1-b2 se intersectan.
        """

        def ccw(p1, p2, p3):
            return (p3.y - p1.y) * (p2.x - p1.x) > (p2.y - p1.y) * (p3.x - p1.x)

        return (ccw(a1, b1, b2) != ccw(a2, b1, b2)) and (
            ccw(a1, a2, b1) != ccw(a1, a2, b2)
        )
