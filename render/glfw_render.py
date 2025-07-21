"""
Renderizador basado en GLFW y PyOpenGL para un minimapa 2D.
"""

from __future__ import annotations
import logging
import math
from typing import Dict, Any, Iterable, Optional

import glfw
from OpenGL.GL import (
    glBegin,
    glEnd,
    glColor3f,
    glVertex2f,
    glVertex3f,
    glLineWidth,
    glClear,
    glClearColor,
    glLoadIdentity,
    glMatrixMode,
    glTranslatef,
    glOrtho,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_PROJECTION,
    GL_MODELVIEW,
    GL_LINES,
    GL_QUADS,
    glGetString,
    GL_VERSION,
    glEnable,
    glDisable,
    GL_DEPTH_TEST,
    glBindTexture,
    glTexCoord2f,
    glTexParameteri,
    glTexParameterf,
    GL_TEXTURE_2D,
    GL_TEXTURE_MIN_FILTER,
    GL_LINEAR_MIPMAP_LINEAR,
)
from OpenGL.GLU import gluPerspective
from OpenGL.raw.GL.VERSION.GL_1_0 import glRotatef

from core.map_data import MapData
from core.player import Player
from core.types import Segment, Vec2
import settings
from .renderer_base import IRenderer
from .glfw_camera import Camera2D
from . import colors
from .texture_manager import Texture

logger = logging.getLogger(__name__)

# Mapeo de teclas de GLFW a acciones del juego
_KEYMAP = {
    glfw.KEY_A: ("turn", -settings.PLAYER_TURN_SPEED_DEG),
    glfw.KEY_D: ("turn", settings.PLAYER_TURN_SPEED_DEG),
    glfw.KEY_W: ("move", settings.PLAYER_SPEED),
    glfw.KEY_S: ("move", -settings.PLAYER_SPEED),
    glfw.KEY_Q: ("strafe", -settings.PLAYER_SPEED / 2),
    glfw.KEY_E: ("strafe", settings.PLAYER_SPEED / 2),
}


class GLFW_OpenGLRenderer(IRenderer):
    """
    Renderizador que usa GLFW para la ventana y el contexto, y PyOpenGL
    para dibujar un minimapa 2D.
    """

    @staticmethod
    def get_GLFW_version() -> str:
        """
        Devuelve la version de la biblioteca GLWF
        """
        return glfw.get_version_string().decode()

    def __init__(
        self,
        width: int,
        height: int,
        caption: str,
        texture_manager: TextureManager,  # Inyectar el gestor
        scale: float = 1.0,
        color_theme: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not glfw.init():
            raise RuntimeError("Fallo al inicializar GLFW")

        self.width = width
        self.height = height

        self.texture_manager = texture_manager

        self.window = glfw.create_window(width, height, caption, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Fallo al crear la ventana GLFW")

        glfw.make_context_current(self.window)
        glEnable(GL_DEPTH_TEST)

        try:
            self.gl_version = glGetString(GL_VERSION).decode()
            # logger.info("OpenGL version: %s", self.gl_version)
        except Exception as e:
            # logger.warning("No se pudo obtener la versión de OpenGL: %s", e)
            self.gl_version = "Unknown"

        glfw.set_window_size_callback(self.window, self._on_resize)
        self.theme = color_theme if color_theme is not None else colors.default_theme()
        self.camera = Camera2D(width=width, height=height, scale=scale)
        self._setup_gl(width, height)

    def _draw_3d_wall(self, seg: Segment) -> None:
        wall_height = seg.height if seg.height is not None else settings.WALL_HEIGHT
        half_height = wall_height / 2.0

        # Coordenadas de textura
        u1 = seg.u_offset / settings.TEXTURE_SCALE
        u2 = (seg.u_offset + seg.length()) / settings.TEXTURE_SCALE
        v1, v2 = 0.0, wall_height / (settings.TEXTURE_SCALE * 2) # Ajustar escala vertical si es necesario

        # Vértices del muro
        p1 = seg.a
        p2 = seg.b

        # Cara frontal
        glTexCoord2f(u1, v1); glVertex3f(p1.x, -half_height, p1.y)
        glTexCoord2f(u2, v1); glVertex3f(p2.x, -half_height, p2.y)
        glTexCoord2f(u2, v2); glVertex3f(p2.x,  half_height, p2.y)
        glTexCoord2f(u1, v2); glVertex3f(p1.x,  half_height, p1.y)

    def get_opengl_version(self) -> str:
        """
        Devuelve la version de OpenGL utilizada
        """
        return self.gl_version

    def _setup_gl(self, width: int, height: int) -> None:
        """Configura el estado inicial de OpenGL para renderizado 2D."""
        bg = self.theme["bg"]
        glClearColor(bg[0] / 255.0, bg[1] / 255.0, bg[2] / 255.0, 1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def _on_resize(self, window, width: int, height: int) -> None:
        """Callback para el redimensionamiento de la ventana."""

        from OpenGL.GL import glViewport

        self.width = width
        self.height = height

        glViewport(0, 0, width, height)

        self.camera.update_viewport(width, height)
        # self._setup_gl(width, height)

    # --- Implementación de la interfaz IRenderer ---

    def is_running(self) -> bool:
        return not glfw.window_should_close(self.window)

    def poll_input(self) -> Dict[str, Any]:
        state: Dict[str, Any] = {"turn": 0.0, "move": 0.0, "strafe": 0.0, "quit": False}

        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            state["quit"] = True
            glfw.set_window_should_close(self.window, True)
            return state

        for key, (action, value) in _KEYMAP.items():
            if glfw.get_key(self.window, key) == glfw.PRESS:
                if action in ("turn", "move", "strafe"):
                    state[action] += value
        return state



    def draw_frame(
        self,
        map_data: MapData,
        player: Player,
        visible_segments: Optional[Iterable[Segment]] = None,
    ) -> None:
        """
        Orquesta el dibujado del mapa en 3D y del overlay del minimapa 2D.
        """

        # Limpar el buffer y la profundidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._setup_3d_projection(player)
        self._draw_3d_world(player, visible_segments)

        if settings.ENABLE_MINIMAP:
            self._setup_2d_projection()
            self._draw_2d_minimap(map_data, player, visible_segments)

        # Actualizar la cámara para centrarse en el jugador
        # self.camera.set_target(player.x, player.y)
        # self.camera.apply_transform()
        # glLoadIdentity()
        # Dibujar el mapa
        # self._draw_map(map_data, visible_segments)
        # self._draw_player(player)

    def _setup_3d_projection(self, player: Player) -> None:
        """
        Configura la mastriz para la vista del jugador
        Args:
             player
        """

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # width, height = glfw.get_window_size(self.window)
        aspect_ratio = self.width / self.height if self.height > 0 else 1.0

        horizontal_fov_rad = math.radians(player.fov_deg)
        vertical_fov_rad = 2 * math.atan(
            math.tan(horizontal_fov_rad / 2) / aspect_ratio
        )
        vertical_fov_deg = math.degrees(vertical_fov_rad)

        # gluPerspective(player.fov_deg, aspect_ratio, 0.1, 2000.0)
        gluPerspective(vertical_fov_deg, aspect_ratio, 0.1, 2000.0)

    def _setup_2d_projection(self) -> None:
        """
        Configura la matriz para la vista 2D
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # width, height = glfw.get_window_size(self.window)
        glOrtho(0, self.width, 0, self.height, -1, 1)

    def _draw_3d_world(
        self,
        player: Player,
        visible_segments: Optional[Iterable[Segment]] = None,
    ) -> None:
        """
        Dibuja el mapa en 3D.
        Args:
            player: El jugador.
            visible_segments: Segmentos visibles.
        """

        # Configurar Camara
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glRotatef(player.angle_deg + 90, 0.0, 1.0, 0.0)
        glTranslatef(-player.x, settings.PLAYER_HEIGHT, -player.y)

        # Dibujar las paredes visibles
        if visible_segments:
            # Agrupar segmentos por textura para optimizar cambios de estado de OpenGL
            segments_by_texture: Dict[Optional[str], list[Segment]] = {}
            for seg in visible_segments:
                tex_name = seg.texture_name
                if tex_name not in segments_by_texture:
                    segments_by_texture[tex_name] = []
                segments_by_texture[tex_name].append(seg)

            # Iterar sobre cada grupo de textura
            for texture_name, segments_group in segments_by_texture.items():
                texture = self.texture_manager.get_texture(texture_name) if texture_name else None

                if texture:
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, texture.id)
                    glColor3f(1.0, 1.0, 1.0)  # Blanco para no teñir la textura
                else:
                    glDisable(GL_TEXTURE_2D)
                    # Color de fallback si no hay textura
                    wall_color = self.theme.get("walls", (200, 200, 200))
                    glColor3f(wall_color[0] / 255.0, wall_color[1] / 255.0, wall_color[2] / 255.0)

                # Dibujar todos los segmentos que usan esta textura
                glBegin(GL_QUADS)
                for seg in segments_group:
                    self._draw_3d_wall(seg)
                glEnd()

            # Restaurar estado
            glDisable(GL_TEXTURE_2D)

    def _draw_3d_wall(self, seg: Segment) -> None:
        """
        Dibuja una pared en 3D.
        Args:
           seg: El segmento de la pared.
        """

        h = settings.WALL_HEIGHT / 2.0
        if not self.wall_texture:
            color = self.theme.get("wall_interior", (255, 255, 255))
            dim_factor = 0.8
            glColor3f(
                color[0] / 255.0 * dim_factor,
                color[1] / 255.0 * dim_factor,
                color[2] / 255.0 * dim_factor,
            )
            # Si no hay textura, no necesitamos hacer más aquí
            glBegin(GL_QUADS)
            glVertex3f(seg.a.x, -h, seg.a.y)
            glVertex3f(seg.b.x, -h, seg.b.y)
            glVertex3f(seg.b.x, h, seg.b.y)
            glVertex3f(seg.a.x, h, seg.a.y)
            glEnd()
            return

        original = seg.original_segment
        if not original:
            return

        texture_world_width = settings.WALL_HEIGHT * settings.TEXTURE_SCALE
        if texture_world_width == 0:
            return

        dist_from_origin_start = (seg.a - original.a).length()

        u_offset_start = original.u_offset + dist_from_origin_start
        u_start = u_offset_start / texture_world_width
        u_end = (u_offset_start + seg.length()) / texture_world_width

        glBegin(GL_QUADS)
        # Vertices en el plano XZ, altura en Y

        # Abajo-Izquierda
        glTexCoord2f(u_start, 0.0)
        glVertex3f(seg.a.x, -h, seg.a.y)

        # Abajo-Derecha
        glTexCoord2f(u_end, 0.0)
        glVertex3f(seg.b.x, -h, seg.b.y)

        # Arriba-Derecha
        glTexCoord2f(u_end, 1.0)
        glVertex3f(seg.b.x, h, seg.b.y)

        # Arriba-Izquierda
        glTexCoord2f(u_start, 1.0)
        glVertex3f(seg.a.x, h, seg.a.y)

        glEnd()

    def _draw_2d_minimap(
        self,
        map_data: MapData,
        player: Player,
        visible_segments: Optional[Iterable[Segment]],
    ) -> None:
        """
        Dibuja el minimapa 2D.
        Args:
            map_data: Los datos del mapa.
            player: El jugador.
            visible_segments: Segmentos visibles.
        """

        # Desavilitar el test de profundidad
        glDisable(GL_DEPTH_TEST)

        # Configurar matrix Ortogafica
        # glMatrixMode(GL_PROJECTION)
        # glLoadIdentity()
        # width, height = glfw.get_window_size(self.window)
        # glOrtho(0, width, 0, height, -1, 1)

        # Configurar matrix de vista
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Camara 2D
        self.camera.set_target(player.x, player.y)
        self.camera.apply_transform()

        # Dibujar el mapa
        self._draw_map(map_data, visible_segments)
        self._draw_player(player)

        # Rehabilitar el test de profundidad
        glEnable(GL_DEPTH_TEST)

    def dispatch_events(self) -> None:
        glfw.poll_events()

    def flip_buffers(self) -> None:
        glfw.swap_buffers(self.window)

    def shutdown(self) -> None:
        logger.info("Cerrando GLFW.")
        glfw.terminate()

    # --- Métodos de dibujo internos (usando OpenGL) ---

    def _draw_map(
        self, map_data: MapData, visible_segments: Optional[Iterable[Segment]]
    ) -> None:
        for seg in map_data.segments:
            self._draw_segment(seg, is_visible=False)
        if visible_segments is not None:
            for seg in visible_segments:
                self._draw_segment(seg, is_visible=True)

    def _draw_segment(self, seg: Segment, is_visible: bool) -> None:
        if is_visible and "visible_wall" in self.theme:
            color = self.theme["visible_wall"]
            width = 3.0
        else:
            color = (
                self.theme["wall_interior"]
                if seg.interior_facing
                else self.theme["wall_exterior"]
            )
            width = 1.0

        glColor3f(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
        glLineWidth(width)
        glBegin(GL_LINES)
        glVertex2f(seg.a.x, seg.a.y)
        glVertex2f(seg.b.x, seg.b.y)
        glEnd()

    def _draw_player(self, player: Player) -> None:
        px, py = player.x, player.y
        color = self.theme["player"]
        glColor3f(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)

        # Dibujar círculo para el jugador (simulado con líneas)
        glBegin(GL_LINES)
        import math

        for i in range(20):
            angle1 = (i / 20) * 2 * math.pi
            angle2 = ((i + 1) / 20) * 2 * math.pi
            glVertex2f(px + math.cos(angle1) * 4, py + math.sin(angle1) * 4)
            glVertex2f(px + math.cos(angle2) * 4, py + math.sin(angle2) * 4)
        glEnd()

        # Dibujar cono de visión (FOV)
        e1, e2 = player.fov_edges()
        color_fov = self.theme["fov"]
        glColor3f(color_fov[0] / 255.0, color_fov[1] / 255.0, color_fov[2] / 255.0)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        glVertex2f(px, py)
        glVertex2f(e1.x, e1.y)
        glVertex2f(px, py)
        glVertex2f(e2.x, e2.y)
        glEnd()
