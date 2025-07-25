"""
VisibilityManager: Clase responsable de calcular los segmentos visibles dentro del FOV usando el BSP.

Aplica filtro angular, distancia y oclusión para determinar la visibilidad de los segmentos.
"""

from __future__ import annotations
from typing import List, Optional
import math

from .types import Segment, Vec2
from .player import Player
from .bsp import BSPNode
from utils.math_utils import line_side

class VisibilityManager:
    """
    Encapsula la lógica de visibilidad del motor 3D.
    Permite activar/desactivar el recorte de paredes por el FOV mediante la propiedad clip_walls_to_fov.
    Permite configurar un margen adicional al corte del FOV con fov_margin_deg.
    El margen se aplica tanto al corte por FOV como al corte por oclusión angular.
    Todos los métodos son estáticos para cumplir SRP y facilitar el testeo.
    """

    # --- NUEVO: Opción global para activar/desactivar el clipping de paredes ---
    clip_walls_to_fov: bool = True
    """
    Si es True, los segmentos de pared se recortan por el triángulo del FOV.
    Si es False, los segmentos se muestran completos si están dentro del FOV.
    Puedes modificar este valor en tiempo de ejecución:
        VisibilityManager.clip_walls_to_fov = False  # para desactivar el clipping
    """

    fov_margin_deg: float = 10.0
    """
    Margen adicional en grados que se suma al ángulo del FOV para el clipping.
    Permite que las paredes se corten con un buffer extra.
    """

    @classmethod
    def set_clip_walls_to_fov(cls, value: bool) -> None:
        """
        Permite activar o desactivar el recorte de paredes por el FOV.
        Args:
            value (bool): True para recortar, False para mostrar completos.
        """
        cls.clip_walls_to_fov = value

    @classmethod
    def set_fov_margin_deg(cls, margin: float) -> None:
        """
        Permite configurar el margen adicional en grados para el corte del FOV.
        Args:
            margin (float): Margen en grados a sumar al FOV.
        """
        cls.fov_margin_deg = margin

    @staticmethod
    def compute_visible_segments(
        root: BSPNode,
        player: Player,
        max_dist: float | None = None,
        clip_to_fov: bool = None,
    ) -> List[Segment]:
        """
        Devuelve los segmentos que caen dentro del FOV angular + rango del jugador.
        El recorte por FOV se controla por la propiedad clip_walls_to_fov o el argumento clip_to_fov.
        El margen adicional se suma al ángulo del FOV y también se aplica al corte por oclusión angular.
        Se optimiza la gestión de oclusión angular para evitar cálculos redundantes y mejorar el rendimiento.
        Args:
            root (BSPNode): Nodo raíz del BSP.
            player (Player): Instancia del jugador.
            max_dist (float | None): Distancia máxima de visibilidad.
            clip_to_fov (bool | None): Si se recorta al FOV (sobrescribe la propiedad de clase si se indica).
        Returns:
            List[Segment]: Lista de segmentos visibles.
        """
        if max_dist is None:
            max_dist = player.fov_length

        clip = (
            clip_to_fov
            if clip_to_fov is not None
            else VisibilityManager.clip_walls_to_fov
        )

        fov_deg_total = player.fov_deg + VisibilityManager.fov_margin_deg
        half = math.radians(fov_deg_total / 2)

        ordered: list[Segment] = []
        VisibilityManager._collect_bsp_order(root, player.pos, ordered)

        pos = player.pos
        max_d2 = max_dist * max_dist
        ang = player.angle_rad
        tri = (
            pos,
            Vec2(
                pos.x + math.cos(ang - half) * max_dist,
                pos.y + math.sin(ang - half) * max_dist,
            ),
            Vec2(
                pos.x + math.cos(ang + half) * max_dist,
                pos.y + math.sin(ang + half) * max_dist,
            ),
        )

        # --- NUEVO: Si el clipping está desactivado, solo filtra por orientación y distancia ---
        if not clip:
            visible: list[Segment] = []
            for seg in ordered:
                if not VisibilityManager._is_segment_facing_player(seg, player.pos):
                    continue
                # Filtrar por distancia máxima (ambos extremos)
                if (
                    (seg.a.x - pos.x) ** 2 + (seg.a.y - pos.y) ** 2 > max_d2
                    and (seg.b.x - pos.x) ** 2 + (seg.b.y - pos.y) ** 2 > max_d2
                ):
                    continue
                visible.append(seg)
            return visible

        # --- Si el clipping está activado, usar el algoritmo completo ---
        # Lista de intervalos angulares cubiertos, ordenada y optimizada
        covered: list[tuple[float, float]] = []
        visible: list[Segment] = []

        for seg in ordered:
            # --- FILTRO: Solo considerar segmentos orientados hacia el jugador ---
            if not VisibilityManager._is_segment_facing_player(seg, player.pos):
                continue  # El jugador está "detrás" de la pared, no es visible

            # Selección de método de recorte según configuración
            if clip:
                clipped_list = VisibilityManager._clip_segment_to_triangle_multi(seg, tri)
            else:
                if VisibilityManager._segment_in_fov(seg, pos, ang, half, max_d2, tri):
                    clipped_list = [seg]
                else:
                    clipped_list = []
            for clipped in clipped_list:
                da = math.atan2(clipped.a.y - pos.y, clipped.a.x - pos.x)
                db = math.atan2(clipped.b.y - pos.y, clipped.b.x - pos.x)
                a0 = VisibilityManager._angle_diff(da, ang)
                a1 = VisibilityManager._angle_diff(db, ang)
                margin_rad = math.radians(VisibilityManager.fov_margin_deg)
                seg_start = min(a0, a1)
                seg_end = max(a0, a1)
                seg_start = max(seg_start, -half - margin_rad)
                seg_end = min(seg_end, half + margin_rad)
                if seg_end <= seg_start:
                    continue

                # --- Optimización de oclusión angular ---
                # Solo calcula los intervalos no cubiertos, evitando solapamientos innecesarios
                intervals = VisibilityManager._subtract_intervals((seg_start, seg_end), covered)
                if not intervals:
                    continue  # Todo el segmento está ocluido, no se procesa

                for ia, ib in intervals:
                    t0 = (ia - a0) / (a1 - a0) if a1 != a0 else 0.0
                    t1 = (ib - a0) / (a1 - a0) if a1 != a0 else 1.0
                    p0 = VisibilityManager._lerp_vec2(clipped.a, clipped.b, t0)
                    p1 = VisibilityManager._lerp_vec2(clipped.a, clipped.b, t1)
                    u0 = VisibilityManager._interpolate_u_offset(seg.original_segment, p0)
                    u1 = VisibilityManager._interpolate_u_offset(seg.original_segment, p1)
                    visible.append(
                        Segment(
                            p0,
                            p1,
                            clipped.interior_facing,
                            u_offset=u0,
                            texture_name=seg.original_segment.texture_name,
                            height=seg.original_segment.height,
                            original_segment=seg.original_segment,
                            polygon_name=seg.original_segment.polygon_name,
                        )
                    )
                    # Añadir el nuevo intervalo cubierto y fusionar para mantener la lista optimizada
                    covered.append((ia, ib))
                # Fusiona los intervalos cubiertos para evitar solapamientos y mantener la lista ordenada
                covered = VisibilityManager._merge_intervals(covered)

        return visible

    @staticmethod
    def _subtract_intervals(interval, covered):
        """Devuelve partes de interval no cubiertas por covered."""
        start, end = interval
        result = []
        curr = start
        for cstart, cend in sorted(covered):
            if cend <= curr:
                continue
            if cstart > end:
                break
            if cstart > curr:
                result.append((curr, min(cstart, end)))
            curr = max(curr, cend)
            if curr >= end:
                break
        if curr < end:
            result.append((curr, end))
        return result

    @staticmethod
    def _merge_intervals(intervals, epsilon=1e-5):
        """
        Une intervalos solapados o adyacentes, considerando un margen de tolerancia (epsilon).
        Esto ayuda a evitar pequeños huecos entre paredes adyacentes por errores de precisión.
        Args:
            intervals (list[tuple[float, float]]): Lista de intervalos (start, end).
            epsilon (float): Margen de tolerancia para fusionar intervalos cercanos.
        Returns:
            list[tuple[float, float]]: Lista de intervalos fusionados.
        """
        if not intervals:
            return []
        # Ordenar los intervalos por el inicio
        intervals = sorted(intervals)
        merged = [intervals[0]]
        for s, e in intervals[1:]:
            last_s, last_e = merged[-1]
            # Si los intervalos se solapan o están muy cerca, fusionarlos
            if s <= last_e + epsilon:
                merged[-1] = (last_s, max(last_e, e))
            else:
                merged.append((s, e))
        return merged

    @staticmethod
    def _clip_segment_to_triangle_multi(seg: Segment, tri: tuple[Vec2, Vec2, Vec2]) -> list[Segment]:
        # Recorta el segmento contra el triángulo FOV y puede devolver 0, 1 o 2 segmentos.
        poly = [seg.a, seg.b]
        for i in range(3):
            a, b = tri[i], tri[(i+1)%3]
            poly = VisibilityManager._clip_poly_against_edge(poly, a, b)
            if not poly or len(poly) < 2:
                return []
        # Si hay más de 2 puntos, hay dos segmentos
        if len(poly) == 2:
            return [seg.replace(a=poly[0], b=poly[1])]
        elif len(poly) == 3:
            return [
                seg.replace(a=poly[0], b=poly[1]),
                seg.replace(a=poly[1], b=poly[2]),
            ]
        else:
            # Raro, pero por seguridad
            return [seg.replace(a=poly[i], b=poly[i+1]) for i in range(len(poly)-1)]

    @staticmethod
    def _clip_segment_to_triangle(seg: Segment, tri: tuple[Vec2, Vec2, Vec2]) -> Segment | None:
        # Recorta el segmento contra el triángulo FOV.
        # Devuelve un nuevo segmento recortado o None si está fuera.
        poly = [seg.a, seg.b]
        for i in range(3):
            a, b = tri[i], tri[(i+1)%3]
            poly = VisibilityManager._clip_poly_against_edge(poly, a, b)
            if not poly or len(poly) < 2:
                return None
        return seg.replace(a=poly[0], b=poly[1])

    @staticmethod
    def _clip_poly_against_edge(poly: list[Vec2], a: Vec2, b: Vec2) -> list[Vec2]:
        # Recorta una lista de puntos contra el semiplano izquierdo de la arista ab
        def inside(p):
            return line_side(p, a, b) >= 0
        out = []
        for i in range(len(poly)):
            curr, prev = poly[i], poly[i-1]
            incurr, inprev = inside(curr), inside(prev)
            if incurr:
                if not inprev:
                    out.append(VisibilityManager._segment_intersection(prev, curr, a, b))
                out.append(curr)
            elif inprev:
                out.append(VisibilityManager._segment_intersection(prev, curr, a, b))
        return out

    @staticmethod
    def _segment_intersection(p1, p2, q1, q2):
        # Calcula la intersección de los segmentos p1p2 y q1q2
        dx1, dy1 = p2.x - p1.x, p2.y - p1.y
        dx2, dy2 = q2.x - q1.x, q2.y - q1.y
        denom = dx1 * dy2 - dy1 * dx2
        if denom == 0:
            return p1  # paralelos, devolver uno arbitrario
        t = ((q1.x - p1.x) * dy2 - (q1.y - p1.y) * dx2) / denom
        return Vec2(p1.x + t * dx1, p1.y + t * dy1)

    @staticmethod
    def _collect_bsp_order(node: Optional[BSPNode], pos: Vec2, out: List[Segment]) -> None:
        """Recorre el BSP cercano→lejano según la posición del jugador."""
        if node is None:
            return
        if node.partition is None:
            return
        side = line_side(pos, node.partition.a, node.partition.b)
        near = node.front if side >= 0 else node.back
        far = node.back if side >= 0 else node.front

        VisibilityManager._collect_bsp_order(near, pos, out)
        out.extend(node.coplanar)
        VisibilityManager._collect_bsp_order(far, pos, out)

    @staticmethod
    def _segment_in_fov(
        seg: Segment,
        pos: Vec2,
        ang: float,
        half: float,
        max_d2: float,
        tri: tuple[Vec2, Vec2, Vec2],
    ) -> bool:
        # extremo dentro
        if VisibilityManager._point_in_fov(seg.a, pos, ang, half, max_d2) or VisibilityManager._point_in_fov(seg.b, pos, ang, half, max_d2):
            return True
        # intersección con triángulo FOV
        if VisibilityManager._segment_intersects_triangle(seg, tri):
            # distancia mínima al jugador
            if VisibilityManager._seg_min_dist2_to_point(seg, pos) <= max_d2:
                return True
        return False

    @staticmethod
    def _point_in_fov(p: Vec2, pos: Vec2, ang: float, half: float, max_d2: float) -> bool:
        dx = p.x - pos.x
        dy = p.y - pos.y
        d2 = dx * dx + dy * dy
        if d2 > max_d2:
            return False
        pa = math.atan2(dy, dx)
        da = VisibilityManager._angle_diff(pa, ang)
        return abs(da) <= half

    @staticmethod
    def _angle_diff(a: float, b: float) -> float:
        d = a - b
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        return d

    @staticmethod
    def _seg_min_dist2_to_point(seg: Segment, p: Vec2) -> float:
        ax = seg.a.x; ay = seg.a.y
        bx = seg.b.x; by = seg.b.y
        px = p.x; py = p.y
        vx = bx - ax; vy = by - ay
        wx = px - ax; wy = py - ay
        c1 = vx * wx + vy * wy
        if c1 <= 0:
            dx = px - ax; dy = py - ay
            return dx*dx + dy*dy
        c2 = vx * vx + vy * vy
        if c2 <= c1:
            dx = px - bx; dy = py - by
            return dx*dx + dy*dy
        t = c1 / c2
        projx = ax + t * vx
        projy = ay + t * vy
        dx = px - projx; dy = py - projy
        return dx*dx + dy*dy

    @staticmethod
    def _segment_intersects_triangle(seg: Segment, tri: tuple[Vec2, Vec2, Vec2]) -> bool:
        a, b = seg.a, seg.b
        t0, t1, t2 = tri
        if VisibilityManager._point_in_triangle(a, tri) or VisibilityManager._point_in_triangle(b, tri):
            return True
        edges = ((t0, t1), (t1, t2), (t2, t0))
        for e_a, e_b in edges:
            if VisibilityManager._segments_intersect(a, b, e_a, e_b):
                return True
        return False

    @staticmethod
    def _point_in_triangle(p: Vec2, tri: tuple[Vec2, Vec2, Vec2]) -> bool:
        a, b, c = tri
        v0x = c.x - a.x; v0y = c.y - a.y
        v1x = b.x - a.x; v1y = b.y - a.y
        v2x = p.x - a.x; v2y = p.y - a.y
        dot00 = v0x*v0x + v0y*v0y
        dot01 = v0x*v1x + v0y*v1y
        dot02 = v0x*v2x + v0y*v2y
        dot11 = v1x*v1x + v1y*v1y
        dot12 = v1x*v2x + v1y*v2y
        denom = dot00 * dot11 - dot01 * dot01
        if denom == 0:
            return False
        inv = 1.0 / denom
        u = (dot11 * dot02 - dot01 * dot12) * inv
        v = (dot00 * dot12 - dot01 * dot02) * inv
        return (u >= 0) and (v >= 0) and (u + v <= 1)

    @staticmethod
    def _segments_intersect(a1: Vec2, a2: Vec2, b1: Vec2, b2: Vec2) -> bool:
        def orient(ax, ay, bx, by, cx, cy):
            return (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
        o1 = orient(a1.x, a1.y, a2.x, a2.y, b1.x, b1.y)
        o2 = orient(a1.x, a1.y, a2.x, a2.y, b2.x, b2.y)
        o3 = orient(b1.x, b1.y, b2.x, b2.y, a1.x, a1.y)
        o4 = orient(b1.x, b1.y, b2.x, b2.y, a2.x, a2.y)

        # colineales
        if o1 == 0 and o2 == 0 and o3 == 0 and o4 == 0:
            return VisibilityManager._on_segment(a1, b1, a2) or VisibilityManager._on_segment(a1, b2, a2) or VisibilityManager._on_segment(b1, a1, b2) or VisibilityManager._on_segment(b1, a2, b2)
        return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)

    @staticmethod
    def _on_segment(a: Vec2, b: Vec2, c: Vec2) -> bool:
        return min(a.x, c.x) <= b.x <= max(a.x, c.x) and min(a.y, c.y) <= b.y <= max(a.y, c.y)

    @staticmethod
    def _lerp_vec2(a: Vec2, b: Vec2, t: float) -> Vec2:
        """Interpolación lineal entre dos Vec2."""
        return Vec2(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)

    @staticmethod
    def _interpolate_u_offset(original: Segment, p: Vec2) -> float:
        """
        Proyecta el punto p sobre el segmento original y calcula el u_offset correspondiente.
        Corrige el sentido de la interpolación para paredes exteriores (interior_facing=False)
        para que el mapeo UV sea coherente tras el clipping.
        """
        ax, ay = original.a.x, original.a.y
        bx, by = original.b.x, original.b.y
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        if length == 0:
            return original.u_offset
        # Calcular t como proyección de p sobre el segmento
        t = ((p.x - ax) * dx + (p.y - ay) * dy) / (length * length)
        t = max(0.0, min(1.0, t))
        # Si la pared es exterior (habitaciones), invertir la interpolación
        if not original.interior_facing:
            t = 1.0 - t
        return original.u_offset + t * length

    @staticmethod
    def _is_segment_facing_player(seg: Segment, player_pos: Vec2) -> bool:
        """
        Determina si el segmento está orientado hacia el jugador.
        Devuelve True si la cara visible del segmento está orientada hacia el jugador,
        False si el jugador está "detrás" de la pared.

        La lógica compara el signo del producto escalar de la normal con la posición del jugador
        y el valor de interior_facing, para que coincida con la convención de orientación.
        """
        # Vector de la pared
        wall_dx = seg.b.x - seg.a.x
        wall_dy = seg.b.y - seg.a.y
        # Vector normal (sentido antihorario respecto a la pared)
        normal_x = -wall_dy
        normal_y = wall_dx
        # Punto medio del segmento
        mid_x = (seg.a.x + seg.b.x) / 2
        mid_y = (seg.a.y + seg.b.y) / 2
        # Vector desde el punto medio hacia el jugador
        to_player_x = player_pos.x - mid_x
        to_player_y = player_pos.y - mid_y
        # Producto escalar entre la normal y el vector al jugador
        dot = normal_x * to_player_x + normal_y * to_player_y

        # La pared es visible si:
        # - interior_facing=True y dot > 0 (jugador en la cara interior)
        # - interior_facing=False y dot < 0 (jugador en la cara exterior)
        # Es decir, el signo de dot debe coincidir con interior_facing
        return (dot > 0) == seg.interior_facing
