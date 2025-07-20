"""
Construcción de BSP Tree 2D.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Sequence
import logging
import random

from .types import Segment, Vec2
from .math_utils import split_segment
from .errors import BSPBuildError

logger = logging.getLogger(__name__)


@dataclass
class BSPNode:
    # línea de partición: tomamos el segmento como representativo de la hiperplano 2D
    partition: Optional[Segment] = None
    coplanar: List[Segment] = field(default_factory=list)
    front: Optional["BSPNode"] = None
    back: Optional["BSPNode"] = None

    def is_leaf(self) -> bool:
        return self.partition is None and not self.front and not self.back


class BSPBuilder:
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
                node.coplanar.append(s)
                continue
            f, b = split_segment(s, partition.a, partition.b)
            if f:
                front_list.extend(f)
            if b:
                back_list.extend(b)

        # recursión
        node.front = self._build_recursive(front_list, depth + 1) if front_list else None
        node.back = self._build_recursive(back_list, depth + 1) if back_list else None
        return node