"""
Loop principal del juego / simulación minimalista con visibilidad.
"""

from __future__ import annotations
import logging
import time

from .map_data import MapData
from .bsp import BSPNode
from .player import Player
from .visibility import compute_visible_segments
from render.renderer_base import IRenderer
from core.collision import CollisionDetector

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, map_data: MapData, bsp_root: BSPNode, player: Player, renderer: IRenderer) -> None:
        self.map_data = map_data
        self.bsp_root = bsp_root
        self.player = player
        self.renderer = renderer
        self._running = False
        self._visible_cache = []
        self.collision = CollisionDetector(bsp_root)

    def run(self) -> None:
        logger.info("Entrando al loop principal.")
        self._running = True
        last_time = time.perf_counter()
        while self._running and self.renderer.is_running():
            now = time.perf_counter()
            dt = now - last_time
            last_time = now

            self._handle_input(dt)
            self._update(dt)

            # calcular visibilidad
            self._visible_cache = compute_visible_segments(self.bsp_root, self.player)

            # dibujar (nota: usamos argumento nombrado para evitar errores por número de params)
            self.renderer.draw_frame(self.map_data, self.player, visible_segments=self._visible_cache)

        logger.info("Loop principal terminado.")

    def stop(self) -> None:
        self._running = False

    def _handle_input(self, dt: float) -> None:
        inp = self.renderer.poll_input()
        if inp.get("quit"):
            self.stop()
            return
        turn = inp.get("turn", 0.0)
        if turn:
            self.player.rotate(turn)
        move = inp.get("move", 0.0)
        strafe = inp.get("strafe", 0.0)
        if move or strafe:
            import math
            ang = math.radians(self.player.angle_deg)
            fx = math.cos(ang); fy = math.sin(ang)
            rx = math.cos(ang + math.pi/2); ry = math.sin(ang + math.pi/2)
            dx = fx * move + rx * strafe
            dy = fy * move + ry * strafe
            start = self.player.pos
            end = type(start)(self.player.x + dx * dt, self.player.y + dy * dt)
            col = self.collision.find_first_collision(start, end)
            if col is not None:
                self.player.x = col.x - dx * dt
                self.player.y = col.y - dy * dt
            else:
                self.player.move(dx * dt, dy * dt)

    def _update(self, dt: float) -> None:  # noqa: ARG002 - dt usado en futuro
        pass