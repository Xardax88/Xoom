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

        try:
            while self._running and self.renderer.is_running():
                now = time.perf_counter()
                # Delta time
                dt = now - last_time
                last_time = now

                # Procesar eventos de la ventana
                self.renderer.dispatch_events()

                # Leer input y actualizar estado del jugador
                self._handle_input(dt)
                self._update(dt)

                # Calcular la lógica del juego (visibilidad)
                self._visible_cache = compute_visible_segments(self.bsp_root, self.player)

                # Dibujar el frame en el buffer oculto
                self.renderer.draw_frame(
                    self.map_data, self.player, visible_segments=self._visible_cache
                )

                # Mostrar el frame en pantalla
                self.renderer.flip_buffers()

        finally:
            self.renderer.shutdown()
            logger.info("Loop principal terminado y recursos liberados.")

    def stop(self) -> None:
        self._running = False

    def _handle_input(self, dt: float) -> None:
        inp = self.renderer.poll_input()
        if inp.get("quit"):
            self.stop()
            return

        # Aplicar input al jugador
        turn = inp.get("turn", 0.0)
        if turn:
            self.player.rotate(turn * dt) # Aplicar dt

        move = inp.get("move", 0.0)
        strafe = inp.get("strafe", 0.0)
        if move or strafe:
            import math
            ang = math.radians(self.player.angle_deg)
            fx = math.cos(ang); fy = math.sin(ang)
            rx = math.cos(ang + math.pi/2); ry = math.sin(ang + math.pi/2)

            # Aplicar dt al vector de movimiento
            dx = (fx * move + rx * strafe) * dt
            dy = (fy * move + ry * strafe) * dt

            start = self.player.pos
            # El final ya tiene dt aplicado
            end = type(start)(self.player.x + dx, self.player.y + dy)

            col = self.collision.find_first_collision(start, end)
            if col is not None:
                # Por el momento solo se detiene al colisionar
                pass
            else:
                self.player.move(dx, dy)

    def _update(self, dt: float) -> None:  # noqa: ARG002 - dt usado en futuro
        pass