"""
Interfaz base para renderers.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Iterable, Optional

from core.map_data import MapData
from core.player import Player
from core.types import Segment


class IRenderer(ABC):
    @abstractmethod
    def is_running(self) -> bool:  # pragma: no cover - interface
        ...

    @abstractmethod
    def poll_input(self) -> Dict[str, Any]:  # pragma: no cover - interface
        ...

    @abstractmethod
    def draw_frame(
        self,
        map_data: MapData,
        player: Player,
        visible_segments: Optional[Iterable[Segment]] = None,
    ) -> None:  # pragma: no cover - interface
        ...
