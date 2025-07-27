"""
Game: Módulo principal del juego que maneja la lógica del bucle de juego, entrada del jugador, colisiones y renderizado.
Este módulo integra los datos del mapa, el árbol BSP, el jugador y el renderizador para ejecutar el juego.
"""

from __future__ import annotations
import logging
import time

from .map_data import MapData
from .bsp import BSPNode
from .player import Player
from .visibility import VisibilityManager
from render.renderer_base import IRenderer
from core.collision import CollisionDetector
import settings

logger = logging.getLogger(__name__)


class Game:
    def __init__(
        self, map_data: MapData, bsp_root: BSPNode, player: Player, renderer: IRenderer
    ) -> None:
        self.map_data = map_data
        self.bsp_root = bsp_root
        self.player = player
        self.renderer = renderer
        self._running = False
        self._visible_cache = []
        self.collision = CollisionDetector(bsp_root)
        # Asegura la referencia cruzada entre BSPNode y MapData para visibilidad y lógica
        if hasattr(self.map_data, "set_bsp_root"):
            self.map_data.set_bsp_root(self.bsp_root)

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
                self._visible_cache = VisibilityManager.compute_visible_segments(
                    self.bsp_root, self.player
                )

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

        turn = inp.get("turn", 0.0)
        if turn:
            self.player.rotate(turn * dt)

        move = inp.get("move", 0.0)
        strafe = inp.get("strafe", 0.0)
        if move or strafe:
            import math

            ang = math.radians(self.player.angle_deg)
            fx = math.cos(ang)
            fy = math.sin(ang)
            rx = math.cos(ang + math.pi / 2)
            ry = math.sin(ang + math.pi / 2)

            dx = (fx * move + rx * strafe) * dt
            dy = (fy * move + ry * strafe) * dt

            start = self.player.pos
            end = type(start)(self.player.x + dx, self.player.y + dy)

            # Usar el radio de colisión del jugador desde settings
            player_radius = getattr(settings, "PLAYER_COLLISION_RADIUS", 16.0)

            # Pasar el radio al detector de colisiones
            col = self.collision.find_first_collision(start, end, radius=player_radius)

            if col is not None:
                # logger.debug("Colisión detectada en: %s", col)
                # Buscar el segmento de pared más cercano a la colisión
                nearest_seg = (
                    self.collision.last_collided_segment
                    if hasattr(self.collision, "last_collided_segment")
                    else None
                )

                if nearest_seg is not None:
                    # Calcular el vector tangente de la pared (normalizado)
                    wall_vec = nearest_seg.b - nearest_seg.a
                    wall_len = math.hypot(wall_vec.x, wall_vec.y)
                    if wall_len > 0:
                        wall_tangent = type(wall_vec)(
                            wall_vec.x / wall_len, wall_vec.y / wall_len
                        )
                        # Proyectar el movimiento original sobre el vector tangente (sliding)
                        move_vec = type(wall_vec)(dx, dy)
                        dot = move_vec.x * wall_tangent.x + move_vec.y * wall_tangent.y
                        slide_dx = wall_tangent.x * dot
                        slide_dy = wall_tangent.y * dot
                        # Intentar mover al jugador en la dirección deslizada
                        slide_end = type(start)(
                            self.player.x + slide_dx, self.player.y + slide_dy
                        )
                        slide_col = self.collision.find_first_collision(
                            start, slide_end, radius=player_radius
                        )
                        if slide_col is None:
                            self.player.move(slide_dx, slide_dy)
                        # Si hay colisión también en el slide, no se mueve
                # Si no hay segmento, no se mueve
            else:
                self.player.move(dx, dy)

    def _update(self, dt: float) -> None:  # noqa: ARG002 - dt usado en futuro
        pass
