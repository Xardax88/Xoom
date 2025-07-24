"""
Collision detection module for a BSP tree.
"""

from core.types import Vec2
from core.bsp import BSPNode
from utils.math_utils import line_side

class CollisionDetector:
    """
    Detecta colisiones entre segmentos y un árbol BSP.

    Args:
        bsp_root (BSPNode): Raíz del árbol BSP que representa el mapa.
    return:
        Vec2 | None: El primer punto de colisión encontrado, o None si no hay colisiones.
    """
    def __init__(self, bsp_root: BSPNode):
        self.bsp_root = bsp_root

    def find_first_collision(self, start: Vec2, end: Vec2) -> Vec2 | None:
        collisions = []

        def traverse(node: BSPNode):
            if node is None or node.partition is None:
                return
            for seg in node.coplanar:
                pt = self.segment_intersection(start, end, seg.a, seg.b)
                if pt is not None and self.is_between(start, end, pt) and self.is_between(seg.a, seg.b, pt):
                    collisions.append(pt)
            side_start = line_side(start, node.partition.a, node.partition.b)
            side_end = line_side(end, node.partition.a, node.partition.b)
            if side_start >= 0 and side_end >= 0:
                traverse(node.front)
            elif side_start <= 0 and side_end <= 0:
                traverse(node.back)
            else:
                traverse(node.front)
                traverse(node.back)

        traverse(self.bsp_root)
        if not collisions:
            return None
        return min(collisions, key=lambda p: (p.x - start.x) ** 2 + (p.y - start.y) ** 2)

    @staticmethod
    def segment_intersection(p1, p2, q1, q2):
        dx1, dy1 = p2.x - p1.x, p2.y - p1.y
        dx2, dy2 = q2.x - q1.x, q2.y - q1.y
        denom = dx1 * dy2 - dy1 * dx2
        if denom == 0:
            return None
        t = ((q1.x - p1.x) * dy2 - (q1.y - p1.y) * dx2) / denom
        u = ((q1.x - p1.x) * dy1 - (q1.y - p1.y) * dx1) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            return Vec2(p1.x + t * dx1, p1.y + t * dy1)
        return None

    @staticmethod
    def is_between(a, b, p, margin=2.0):
        minx, maxx = sorted([a.x, b.x])
        miny, maxy = sorted([a.y, b.y])
        return minx - margin <= p.x <= maxx + margin and miny - margin <= p.y <= maxy + margin