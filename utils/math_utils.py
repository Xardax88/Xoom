"""
Funciones matemáticas auxiliares.
"""

from __future__ import annotations
from typing import Iterable, List
from core.types import Vec2, Segment
import math


def polygon_area_signed(points: Iterable[Vec2]) -> float:
    pts = list(points)
    if len(pts) < 3:
        return 0.0
    area = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i].x, pts[i].y
        x2, y2 = pts[(i + 1) % len(pts)].x, pts[(i + 1) % len(pts)].y
        area += (x1 * y2) - (x2 * y1)
    return area / 2.0


def is_clockwise(points: Iterable[Vec2]) -> bool:
    return polygon_area_signed(points) < 0  # convención: área negativa = CW


def segment_length(seg: Segment) -> float:
    dx = seg.b.x - seg.a.x
    dy = seg.b.y - seg.a.y
    return math.hypot(dx, dy)


def line_side(p: Vec2, a: Vec2, b: Vec2) -> float:
    """
    Devuelve >0 si p está a la izquierda de la línea AB, <0 a la derecha, 0 en la línea.
    Usamos convención estándar (ccw positivo).
    """
    return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)


def split_segment(seg: Segment, a: Vec2, b: Vec2):
    """Divide un segmento por la línea (a,b) si cruza. Devuelve (front, back) listas de 0 o 1 segmentos."""
    from_point = line_side(seg.a, a, b)
    to_point = line_side(seg.b, a, b)

    if from_point >= 0 and to_point >= 0:
        return [seg], []  # todo frente
    if from_point <= 0 and to_point <= 0:
        return [], [seg]  # todo atrás

    # cruza la línea -> encontrar intersección
    denom = (seg.b.x - seg.a.x) * (b.y - a.y) - (seg.b.y - seg.a.y) * (b.x - a.x)
    if denom == 0:  # líneas paralelas -> asignar arbitrariamente al frente
        return [seg], []
    t = ((a.x - seg.a.x) * (b.y - a.y) - (a.y - seg.a.y) * (b.x - a.x)) / denom
    ix = seg.a.x + t * (seg.b.x - seg.a.x)
    iy = seg.a.y + t * (seg.b.y - seg.a.y)
    inter = Vec2(ix, iy)

    front_seg = Segment(seg.a, inter, seg.interior_facing)
    back_seg = Segment(inter, seg.b, seg.interior_facing)

    if from_point > 0:
        return [front_seg], [back_seg]
    else:
        return [back_seg], [front_seg]
