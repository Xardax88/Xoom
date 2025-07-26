"""
Construcción de BSP Tree 2D.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Sequence
import logging
import random

from ._types import Segment, Vec2
from utils.math_utils import split_segment
from .errors import BSPBuildError

logger = logging.getLogger(__name__)


@dataclass
class BSPNode:
    # línea de partición: tomamos el segmento como representativo de la hiperplano 2D
    partition: Optional[Segment] = None
    coplanar: List[Segment] = field(default_factory=list)
    front: Optional["BSPNode"] = None
    back: Optional["BSPNode"] = None
    map_data: "MapData" = (
        None  # Referencia al MapData asociado para visibilidad y lógica de juego
    )

    def is_leaf(self) -> bool:
        return self.partition is None and not self.front and not self.back


class BSPBuilder:
    """
    Constructor de un árbol BSP 2D.

    Arg:
        max_depth (int): Profundidad máxima del árbol. Por defecto 32.
        strategy (str): Estrategia de selección de partición. Puede ser "first" o "random".
    """

    def __init__(self, max_depth: int = 32, strategy: str = "first") -> None:
        self.max_depth = max_depth
        self.strategy = strategy

    def build(self, segs: Sequence[Segment]) -> BSPNode:
        logger.debug("Construyendo BSP con %s segmentos", len(segs))
        return self._build_recursive(list(segs), depth=0)

    def _choose_partition(self, segs: List[Segment]) -> Segment:
        if not segs:
            raise BSPBuildError("No hay segmentos para elegir partición")
        if self.strategy == "random":
            return random.choice(segs)
        # otras estrategias futuras: median, longest...
        return segs[0]  # first

    def _build_recursive(self, segs: List[Segment], depth: int) -> BSPNode:
        if depth > self.max_depth or not segs:
            return BSPNode()

        partition = self._choose_partition(segs)
        node = BSPNode(partition=partition)

        front_list: List[Segment] = []
        back_list: List[Segment] = []

        # clasificación
        for s in segs:

            if s is partition:
                node.coplanar.append(s.replace())
                continue

            front_parts, back_parts = split_segment(s, partition.a, partition.b)

            if front_parts is None and back_parts is None:
                # el segmento no cruza la partición, se queda en coplanar
                node.coplanar.append(s.replace())
                continue

            if front_parts:
                front_list.extend(
                    [s.replace(a=part.a, b=part.b) for part in front_parts]
                )
                # front_list.extend(front_parts)
            if back_parts:
                back_list.extend([s.replace(a=part.a, b=part.b) for part in back_parts])
                # back_list.extend(back_parts)

        # recursión
        node.front = (
            self._build_recursive(front_list, depth + 1) if front_list else None
        )
        node.back = self._build_recursive(back_list, depth + 1) if back_list else None
        return node
