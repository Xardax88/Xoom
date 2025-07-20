"""
Renderer basado en Pygame para un minimapa 2D simple con resaltado de paredes visibles.
"""

from __future__ import annotations
import logging
from typing import Dict, Any, Iterable, Optional

import pygame

from core.map_data import MapData
from core.player import Player
from core.types import Segment
from settings import PLAYER_SPEED, PLAYER_TURN_SPEED_DEG
from .renderer_base import IRenderer
from .camera import MiniMapCamera
from . import colors

logger = logging.getLogger(__name__)


_KEYMAP = {
    pygame.K_ESCAPE: ("quit", True),
    pygame.K_a: ("turn", -PLAYER_TURN_SPEED_DEG),
    pygame.K_d: ("turn", PLAYER_TURN_SPEED_DEG),
    pygame.K_w: ("move", PLAYER_SPEED),
    pygame.K_s: ("move", -PLAYER_SPEED),
    pygame.K_q: ("strafe", -10.0),
    pygame.K_e: ("strafe", 10.0),
}


class PygameRenderer(IRenderer):
    def __init__(
        self,
        width: int,
        height: int,
        fps: int,
        scale: float,
        margin: int,
        color_theme=None,
    ) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Xoom - Minimap")
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.camera = MiniMapCamera(
            width=width, height=height, scale=scale, margin=margin
        )
        self._running = True
        self.theme = color_theme if color_theme is not None else colors.default_theme()

    def is_running(self) -> bool:
        return self._running

    def poll_input(self) -> Dict[str, Any]:
        state: Dict[str, Any] = {"turn": 0.0, "move": 0.0, "strafe": 0.0, "quit": False}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state["quit"] = True
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state["quit"] = True
                self._running = False

        keys = pygame.key.get_pressed()
        for k, (action, value) in _KEYMAP.items():
            if keys[k]:
                if action in ("turn", "move", "strafe"):
                    state[action] += value
                elif action == "quit":
                    state["quit"] = True
        return state

    def draw_frame(
        self,
        map_data: MapData,
        player: Player,
        visible_segments: Optional[Iterable[Segment]] = None,
    ) -> None:
        self.screen.fill(self.theme["bg"])
        self._draw_map(map_data, visible_segments)
        self._draw_player(player)
        pygame.display.flip()
        self.clock.tick(self.fps)

    # --- Internos ---------------------------------------------------------
    def _draw_map(
        self, map_data: MapData, visible_segments: Optional[Iterable[Segment]]
    ) -> None:
        for seg in map_data.segments:
            self._draw_segment(seg, is_visible=False)
        # Luego dibuja los segmentos visibles (clipped) encima, resaltados
        if visible_segments is not None:
            for seg in visible_segments:
                self._draw_segment(seg, is_visible=True)

    def _draw_segment(self, seg: Segment, is_visible: bool) -> None:
        if is_visible and "visible_wall" in self.theme:
            color = self.theme["visible_wall"]
            width = 2
        else:
            color = (
                self.theme["wall_interior"]
                if seg.interior_facing
                else self.theme["wall_exterior"]
            )
            width = 1
        a = self.camera.world_to_screen(seg.a.x, seg.a.y)
        b = self.camera.world_to_screen(seg.b.x, seg.b.y)
        pygame.draw.line(self.screen, color, a, b, width=width)

    def _draw_player(self, player: Player) -> None:
        px, py = self.camera.world_to_screen(player.x, player.y)
        pygame.draw.circle(self.screen, self.theme["player"], (px, py), 3)
        e1, e2 = player.fov_edges()
        e1s = self.camera.world_to_screen(e1.x, e1.y)
        e2s = self.camera.world_to_screen(e2.x, e2.y)
        pygame.draw.line(self.screen, self.theme["fov"], (px, py), e1s, width=1)
        pygame.draw.line(self.screen, self.theme["fov"], (px, py), e2s, width=1)
