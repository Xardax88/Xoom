"""
Módulo de detección de colisiones para un árbol BSP.
Detecta colisiones considerando el radio del jugador como un círculo.
"""

from core.types import Vec2
from core.bsp import BSPNode
from utils.math_utils import line_side
import math

class CollisionDetector:
    """
    Detecta colisiones entre el trayecto de un círculo (jugador) y los muros del BSP.
    El radio define el tamaño del círculo de colisión.
    """

    def __init__(self, bsp_root: BSPNode):
        self.bsp_root = bsp_root
        self.last_collided_segment = None  # Guarda el último segmento con el que se colisionó

    def find_first_collision(self, start: Vec2, end: Vec2, radius: float = 0.0) -> Vec2 | None:
        """
        Busca la primera colisión entre el trayecto de un círculo (jugador) y los muros del BSP.
        Además, guarda el segmento con el que se colisionó para sliding.
        """
        collisions = []

        # Limpiar el último segmento colisionado antes de buscar
        self.last_collided_segment = None

        def traverse(node: BSPNode):
            if node is None or node.partition is None:
                return
            for seg in node.coplanar:
                pt = self.segment_moving_circle_collision(start, end, seg.a, seg.b, radius)
                if pt is not None and self.is_between(start, end, pt):
                    collisions.append((pt, seg))
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
        # Seleccionar el punto de colisión más cercano al inicio
        pt, seg = min(collisions, key=lambda pair: (pair[0].x - start.x) ** 2 + (pair[0].y - start.y) ** 2)
        self.last_collided_segment = seg  # Guardar el segmento para sliding
        return pt

    @staticmethod
    def segment_moving_circle_collision(p1, p2, q1, q2, radius):
        """
        Detecta si un círculo de radio 'radius' moviéndose de p1 a p2 colisiona con el segmento q1-q2.
        Si hay colisión, retorna el punto más cercano antes de la colisión.
        Se comprueba la colisión desde ambos lados del segmento para soportar paredes interiores y exteriores.
        """
        # Vector de movimiento del círculo
        d = Vec2(p2.x - p1.x, p2.y - p1.y)
        # Vector del segmento del muro
        f = Vec2(q2.x - q1.x, q2.y - q1.y)
        seg_len2 = f.x * f.x + f.y * f.y

        # Si el segmento es un punto
        if seg_len2 == 0:
            return CollisionDetector.moving_circle_point_collision(p1, p2, q1, radius)

        # --- Comprobar colisión con ambas normales del segmento ---
        # Esto permite detectar colisión desde ambos lados de la pared (interior y exterior)
        col_points = []

        for normal_sign in (+1, -1):
            # Calculamos la normal del segmento en ambos sentidos
            nx = normal_sign * -(q2.y - q1.y)
            ny = normal_sign * (q2.x - q1.x)
            nlen = math.hypot(nx, ny)
            if nlen == 0:
                continue
            nx /= nlen
            ny /= nlen

            # Distancia inicial desde el círculo al segmento (proyectado en la normal)
            dist0 = ((p1.x - q1.x) * nx + (p1.y - q1.y) * ny)
            dist1 = ((p2.x - q1.x) * nx + (p2.y - q1.y) * ny)

            # Si el círculo cruza el segmento (en la normal)
            if (dist0 > radius and dist1 < radius) or (dist0 < -radius and dist1 > -radius):
                # Calculamos el t donde ocurre la colisión
                t = (dist0 - radius) / (dist0 - dist1)
                if 0.0 <= t <= 1.0:
                    # Calculamos el punto de colisión
                    col_x = p1.x + d.x * t
                    col_y = p1.y + d.y * t
                    # Verificamos si el punto proyectado cae dentro del segmento
                    proj = ((col_x - q1.x) * (q2.x - q1.x) + (col_y - q1.y) * (q2.y - q1.y)) / seg_len2
                    if 0.0 <= proj <= 1.0:
                        col_points.append(Vec2(col_x, col_y))

        # También comprobamos colisión con los extremos del segmento (puntos q1 y q2)
        pt1 = CollisionDetector.moving_circle_point_collision(p1, p2, q1, radius)
        pt2 = CollisionDetector.moving_circle_point_collision(p1, p2, q2, radius)
        if pt1:
            col_points.append(pt1)
        if pt2:
            col_points.append(pt2)

        # Retornar el punto de colisión más cercano al inicio, si existe
        if col_points:
            return min(col_points, key=lambda p: (p.x - p1.x) ** 2 + (p.y - p1.y) ** 2)
        return None

    @staticmethod
    def moving_circle_point_collision(p1, p2, point, radius):
        """
        Detecta colisión entre un círculo moviéndose de p1 a p2 y un punto fijo.
        Retorna el punto de colisión si ocurre, o None.
        """
        # Vector de movimiento
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        fx = p1.x - point.x
        fy = p1.y - point.y

        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - radius * radius

        discriminant = b * b - 4 * a * c
        if discriminant < 0 or a == 0:
            return None  # No hay colisión

        discriminant = math.sqrt(discriminant)
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        # Buscamos el primer t válido en [0,1]
        t = None
        if 0.0 <= t1 <= 1.0:
            t = t1
        elif 0.0 <= t2 <= 1.0:
            t = t2

        if t is not None:
            col_x = p1.x + dx * t
            col_y = p1.y + dy * t
            return Vec2(col_x, col_y)
        return None

    @staticmethod
    def closest_point_on_segment(a: Vec2, b: Vec2, p: Vec2) -> Vec2:
        """
        Devuelve el punto más cercano a p sobre el segmento ab.
        """
        ab = Vec2(b.x - a.x, b.y - a.y)
        ab_len2 = ab.x * ab.x + ab.y * ab.y
        if ab_len2 == 0:
            return a
        t = ((p.x - a.x) * ab.x + (p.y - a.y) * ab.y) / ab_len2
        t = max(0, min(1, t))
        return Vec2(a.x + ab.x * t, a.y + ab.y * t)

    @staticmethod
    def is_between(a, b, p, margin=2.0):
        # Verifica si el punto p está entre a y b (con margen)
        minx, maxx = sorted([a.x, b.x])
        miny, maxy = sorted([a.y, b.y])
        return minx - margin <= p.x <= maxx + margin and miny - margin <= p.y <= maxy + margin