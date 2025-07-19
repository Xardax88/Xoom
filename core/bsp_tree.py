#########################################################################
# core/bsp_tree.py - Árbol BSP para partición del espacio
#########################################################################

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from utils.math_utils import Vector2D
from utils.logger import get_logger


class IBSPNode(ABC):
    """Interface para nodos del árbol BSP"""

    @abstractmethod
    def is_leaf(self) -> bool:
        pass


class BSPNode(IBSPNode):
    """Nodo del árbol BSP"""

    def __init__(self):
        self.line_start: Optional[Vector2D] = None
        self.line_end: Optional[Vector2D] = None
        self.front: Optional["BSPNode"] = None
        self.back: Optional["BSPNode"] = None
        self.polygons: List[List[Vector2D]] = []

    def is_leaf(self) -> bool:
        return self.front is None and self.back is None


class BSPTree:
    """Árbol de Partición Binaria del Espacio para renderizado eficiente"""

    def __init__(self):
        self.root: Optional[BSPNode] = None
        self.logger = get_logger()

    def build_tree(self, polygons: List[List[Vector2D]]) -> None:
        """Construir el árbol BSP a partir de una lista de polígonos"""
        if not polygons:
            self.logger.warning("No hay polígonos para construir el árbol BSP")
            return

        self.logger.info(f"Construyendo árbol BSP con {len(polygons)} polígonos")
        self.root = self._build_node(polygons.copy())
        self.logger.info("Árbol BSP construido exitosamente")

    def _build_node(self, polygons: List[List[Vector2D]]) -> Optional[BSPNode]:
        """Construir un nodo del árbol BSP recursivamente"""
        if not polygons:
            return None

        node = BSPNode()

        # Si solo hay un polígono, crear nodo hoja
        if len(polygons) == 1:
            node.polygons = polygons
            return node

        # Seleccionar la mejor línea divisoria (primera línea del primer polígono por simplicidad)
        splitter_polygon = polygons[0]
        if len(splitter_polygon) < 2:
            node.polygons = polygons
            return node

        node.line_start = splitter_polygon[0]
        node.line_end = splitter_polygon[1]

        # Dividir polígonos en frente y atrás
        front_polygons = []
        back_polygons = []

        for i, polygon in enumerate(polygons):
            if i == 0:  # Saltar el polígono divisor
                continue

            side = self._classify_polygon(polygon, node.line_start, node.line_end)

            if side >= 0:  # Frente o coplanar
                front_polygons.append(polygon)
            else:  # Atrás
                back_polygons.append(polygon)

        # Agregar el polígono divisor al nodo actual
        node.polygons = [splitter_polygon]

        # Construir subárboles recursivamente
        node.front = self._build_node(front_polygons)
        node.back = self._build_node(back_polygons)

        return node

    def _classify_polygon(
        self, polygon: List[Vector2D], line_start: Vector2D, line_end: Vector2D
    ) -> int:
        """
        Clasificar un polígono respecto a una línea
        Retorna: 1 si está al frente, -1 si está atrás, 0 si es coplanar
        """
        if len(polygon) == 0:
            return 0

        # Usar el primer vértice del polígono para la clasificación
        point = polygon[0]

        # Calcular el producto cruzado para determinar el lado
        dx1 = line_end[0] - line_start[0]
        dy1 = line_end[1] - line_start[1]
        dx2 = point[0] - line_start[0]
        dy2 = point[1] - line_start[1]

        cross_product = dx1 * dy2 - dy1 * dx2

        if cross_product > 0.001:
            return 1  # Frente
        elif cross_product < -0.001:
            return -1  # Atrás
        else:
            return 0  # Coplanar

    def get_render_order(self, view_point: Vector2D) -> List[List[Vector2D]]:
        """Obtener los polígonos en orden de renderizado desde un punto de vista"""
        if self.root is None:
            return []

        result = []
        self._traverse_for_rendering(self.root, view_point, result)
        return result

    def _traverse_for_rendering(
        self,
        node: Optional[BSPNode],
        view_point: Vector2D,
        result: List[List[Vector2D]],
    ) -> None:
        """Recorrer el árbol en orden para renderizado correcto"""
        if node is None:
            return

        if node.is_leaf():
            result.extend(node.polygons)
            return

        # Determinar desde qué lado está viendo el observador
        side = self._classify_polygon([view_point], node.line_start, node.line_end)

        if side >= 0:  # Observador está al frente
            # Renderizar primero la parte trasera, luego el nodo, luego el frente
            self._traverse_for_rendering(node.back, view_point, result)
            result.extend(node.polygons)
            self._traverse_for_rendering(node.front, view_point, result)
        else:  # Observador está atrás
            # Renderizar primero el frente, luego el nodo, luego la parte trasera
            self._traverse_for_rendering(node.front, view_point, result)
            result.extend(node.polygons)
            self._traverse_for_rendering(node.back, view_point, result)
