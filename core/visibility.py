"""
Cálculo de segmentos visibles dentro del FOV usando el BSP.

Esto es un filtro angular + distancia + oclussion.
"""

from __future__ import annotations
from typing import List, Optional, Iterable
import math

from .types import Segment, Vec2
from .player import Player
from .bsp import BSPNode
from .math_utils import line_side


def compute_visible_segments(
    root: BSPNode,
    player: Player,
    max_dist: float | None = None,
) -> List[Segment]:
    """Devuelve los segmentos que caen dentro del FOV angular + rango del jugador."""
    if max_dist is None:
        max_dist = player.fov_length

    ordered: list[Segment] = []
    _collect_bsp_order(root, player.pos, ordered)

    pos = player.pos
    max_d2 = max_dist * max_dist
    ang = player.angle_rad
    half = math.radians(player.fov_deg / 2)
    tri = (pos, *player.fov_edges())

    covered: list[tuple[float, float]] = []  # intervalos angulares ya cubiertos
    visible: list[Segment] = []

    for seg in ordered:
        clipped_list = _clip_segment_to_triangle_multi(seg, tri)
        for clipped in clipped_list:
            if _seg_min_dist2_to_point(clipped, pos) > max_d2:
                continue
            # Calcular ángulos de los extremos respecto al jugador
            a1 = math.atan2(clipped.a.y - pos.y, clipped.a.x - pos.x)
            a2 = math.atan2(clipped.b.y - pos.y, clipped.b.x - pos.x)
            # Normalizar a [-pi, pi]
            a1 = _angle_diff(a1, ang) + ang
            a2 = _angle_diff(a2, ang) + ang
            seg_start = min(a1, a2)
            seg_end = max(a1, a2)
            # Recortar al FOV
            fov_start = ang - half
            fov_end = ang + half
            seg_start = max(seg_start, fov_start)
            seg_end = min(seg_end, fov_end)
            if seg_end <= seg_start:
                continue
            # Recortar contra intervalos cubiertos
            intervals = _subtract_intervals((seg_start, seg_end), covered)
            for istart, iend in intervals:
                # Interpolar puntos visibles sobre el segmento
                t0 = (istart - a1) / (a2 - a1) if a2 != a1 else 0.0
                t1 = (iend - a1) / (a2 - a1) if a2 != a1 else 1.0
                p0 = Vec2(
                    clipped.a.x + (clipped.b.x - clipped.a.x) * t0,
                    clipped.a.y + (clipped.b.y - clipped.a.y) * t0,
                    )
                p1 = Vec2(
                    clipped.a.x + (clipped.b.x - clipped.a.x) * t1,
                    clipped.a.y + (clipped.b.y - clipped.a.y) * t1,
                    )
                visible.append(Segment(p0, p1, clipped.interior_facing))
                covered.append((istart, iend))
            # Unir y ordenar intervalos cubiertos para eficiencia
            covered = _merge_intervals(covered)
    return visible

# ---------------------------------------------------------------------------
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

def _merge_intervals(intervals):
    """Une intervalos solapados."""
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))
    return merged
# ---------------------------------------------------------------------------

def _clip_segment_to_triangle_multi(seg: Segment, tri: tuple[Vec2, Vec2, Vec2]) -> list[Segment]:
    # Recorta el segmento contra el triángulo FOV y puede devolver 0, 1 o 2 segmentos.
    poly = [seg.a, seg.b]
    for i in range(3):
        a, b = tri[i], tri[(i+1)%3]
        poly = _clip_poly_against_edge(poly, a, b)
        if not poly or len(poly) < 2:
            return []
    # Si hay más de 2 puntos, hay dos segmentos
    if len(poly) == 2:
        return [Segment(poly[0], poly[1], seg.interior_facing)]
    elif len(poly) == 3:
        return [
            Segment(poly[0], poly[1], seg.interior_facing),
            Segment(poly[1], poly[2], seg.interior_facing),
        ]
    else:
        # Raro, pero por seguridad
        return [Segment(poly[i], poly[i+1], seg.interior_facing) for i in range(len(poly)-1)]

def _clip_segment_to_triangle(seg: Segment, tri: tuple[Vec2, Vec2, Vec2]) -> Segment | None:
    # Recorta el segmento contra el triángulo FOV.
    # Devuelve un nuevo segmento recortado o None si está fuera.
    poly = [seg.a, seg.b]
    for i in range(3):
        a, b = tri[i], tri[(i+1)%3]
        poly = _clip_poly_against_edge(poly, a, b)
        if not poly or len(poly) < 2:
            return None
    return Segment(poly[0], poly[1], seg.interior_facing)

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
                out.append(_segment_intersection(prev, curr, a, b))
            out.append(curr)
        elif inprev:
            out.append(_segment_intersection(prev, curr, a, b))
    return out

def _segment_intersection(p1, p2, q1, q2):
    # Calcula la intersección de los segmentos p1p2 y q1q2
    dx1, dy1 = p2.x - p1.x, p2.y - p1.y
    dx2, dy2 = q2.x - q1.x, q2.y - q1.y
    denom = dx1 * dy2 - dy1 * dx2
    if denom == 0:
        return p1  # paralelos, devolver uno arbitrario
    t = ((q1.x - p1.x) * dy2 - (q1.y - p1.y) * dx2) / denom
    return Vec2(p1.x + t * dx1, p1.y + t * dy1)

def _collect_bsp_order(node: Optional[BSPNode], pos: Vec2, out: List[Segment]) -> None:
    """Recorre el BSP cercano→lejano según la posición del jugador."""
    if node is None:
        return
    if node.partition is None:
        return
    side = line_side(pos, node.partition.a, node.partition.b)
    near = node.front if side >= 0 else node.back
    far = node.back if side >= 0 else node.front

    _collect_bsp_order(near, pos, out)
    out.extend(node.coplanar)
    _collect_bsp_order(far, pos, out)


# ---------------------------------------------------------------------------

def _segment_in_fov(
    seg: Segment,
    pos: Vec2,
    ang: float,
    half: float,
    max_d2: float,
    tri: tuple[Vec2, Vec2, Vec2],
) -> bool:
    # extremo dentro
    if _point_in_fov(seg.a, pos, ang, half, max_d2) or _point_in_fov(seg.b, pos, ang, half, max_d2):
        return True
    # intersección con triángulo FOV
    if _segment_intersects_triangle(seg, tri):
        # distancia mínima al jugador
        if _seg_min_dist2_to_point(seg, pos) <= max_d2:
            return True
    return False


def _point_in_fov(p: Vec2, pos: Vec2, ang: float, half: float, max_d2: float) -> bool:
    dx = p.x - pos.x
    dy = p.y - pos.y
    d2 = dx * dx + dy * dy
    if d2 > max_d2:
        return False
    pa = math.atan2(dy, dx)
    da = _angle_diff(pa, ang)
    return abs(da) <= half


def _angle_diff(a: float, b: float) -> float:
    d = a - b
    while d > math.pi:
        d -= 2 * math.pi
    while d < -math.pi:
        d += 2 * math.pi
    return d


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


def _segment_intersects_triangle(seg: Segment, tri: tuple[Vec2, Vec2, Vec2]) -> bool:
    a, b = seg.a, seg.b
    t0, t1, t2 = tri
    if _point_in_triangle(a, tri) or _point_in_triangle(b, tri):
        return True
    edges = ((t0, t1), (t1, t2), (t2, t0))
    for e_a, e_b in edges:
        if _segments_intersect(a, b, e_a, e_b):
            return True
    return False


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


def _segments_intersect(a1: Vec2, a2: Vec2, b1: Vec2, b2: Vec2) -> bool:
    def orient(ax, ay, bx, by, cx, cy):
        return (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
    o1 = orient(a1.x, a1.y, a2.x, a2.y, b1.x, b1.y)
    o2 = orient(a1.x, a1.y, a2.x, a2.y, b2.x, b2.y)
    o3 = orient(b1.x, b1.y, b2.x, b2.y, a1.x, a1.y)
    o4 = orient(b1.x, b1.y, b2.x, b2.y, a2.x, a2.y)

    # colineales
    if o1 == 0 and o2 == 0 and o3 == 0 and o4 == 0:
        return _on_segment(a1, b1, a2) or _on_segment(a1, b2, a2) or _on_segment(b1, a1, b2) or _on_segment(b1, a2, b2)
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


def _on_segment(a: Vec2, b: Vec2, c: Vec2) -> bool:
    return min(a.x, c.x) <= b.x <= max(a.x, c.x) and min(a.y, c.y) <= b.y <= max(a.y, c.y)