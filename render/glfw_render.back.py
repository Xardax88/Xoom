"""
render/glfw_render.py
Renderizador que utiliza GLFW para la ventana y PyOpenGL para el renderizado 2D del minimapa
"""

from __future__ import annotations
import logging
import math
import numpy as np
from typing import Dict, Any, Iterable, Optional

import glfw


from OpenGL.GL import shaders
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from OpenGL.raw.GL.VERSION.GL_1_0 import glRotatef

from core.map_data import MapData
from core.player import Player
from core.types import Segment, Vec2
import settings
from .renderer_base import IRenderer
from .glfw_camera import Camera2D
from . import colors
from core.texture_manager import TextureManager


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


def load_shader_source(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


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

    def _init_shaders(self):
        vertex_src = load_shader_source("assets/shaders/wall.vert")
        fragment_src = load_shader_source("assets/shaders/wall.frag")
        self.shader_program = shaders.compileProgram(
            shaders.compileShader(vertex_src, GL_VERTEX_SHADER),
            shaders.compileShader(fragment_src, GL_FRAGMENT_SHADER),
        )

    def __init__(
        self,
        width: int,
        height: int,
        caption: str,
        scale: float = 1.0,
        color_theme: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not glfw.init():
            raise RuntimeError("Fallo al inicializar GLFW")

        # Configurar opciones de la ventana GLFW
        glfw.window_hint(glfw.DOUBLEBUFFER, True)
        glfw.window_hint(glfw.RESIZABLE, True)
        # glfw.swap_interval(1)

        self.texture_manager = TextureManager()

        self.width = width
        self.height = height

        self.window = glfw.create_window(width, height, caption, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Fallo al crear la ventana GLFW")

        glfw.make_context_current(self.window)
        glEnable(GL_DEPTH_TEST)
        # Activar el cull face para ocultar las caras traseras
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        self._init_shaders()

        try:
            self.gl_version = glGetString(GL_VERSION).decode()
        except Exception as e:
            self.gl_version = "Unknown"

        glfw.set_window_size_callback(self.window, self._on_resize)
        self.theme = color_theme if color_theme is not None else colors.default_theme()
        self.camera = Camera2D(width=width, height=height, scale=scale)
        self._setup_gl(width, height)

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
        state = {
            "turn": 0.0,
            "move": 0.0,
            "strafe": 0.0,
            "quit": False,
            "up": False,
            "down": False,
            "select": False,
        }
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            state["quit"] = True
            glfw.set_window_should_close(self.window, True)
            return state
        if glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS:
            state["down"] = True
        if glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS:
            state["up"] = True
        if (
            glfw.get_key(self.window, glfw.KEY_ENTER) == glfw.PRESS
            or glfw.get_key(self.window, glfw.KEY_KP_ENTER) == glfw.PRESS
        ):
            state["select"] = True

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
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        self._setup_3d_projection(player)
        self._draw_3d_world(player, visible_segments)
        self._draw_grid()

        if settings.ENABLE_MINIMAP:
            self._setup_2d_projection()
            self._draw_2d_minimap(map_data, player, visible_segments)

    def _setup_3d_projection(self, player: Player) -> None:
        """
        Configura la mastriz para la vista del jugador
        Args:
             player
        """

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect_ratio = self.width / self.height if self.height > 0 else 1.0

        horizontal_fov_rad = math.radians(player.fov_deg)
        vertical_fov_rad = 2 * math.atan(
            math.tan(horizontal_fov_rad / 2) / aspect_ratio
        )
        vertical_fov_deg = math.degrees(vertical_fov_rad)

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
        # glDepthFunc(GL_LESS)
        glLoadIdentity()

        glRotatef(player.angle_deg + 90, 0.0, 1.0, 0.0)
        glTranslatef(-player.x, -settings.PLAYER_HEIGHT, -player.y)

        # Dibujar las paredes visibles
        if visible_segments:
            for seg in visible_segments:
                self._draw_3d_wall(seg)

    def _draw_3d_wall_back(self, seg: Segment) -> None:
        """
        Dibuja una pared en 3D.
        """
        # logger.debug(f"Dibujando pared con textura: {seg.texture_name}")

        h = seg.height if seg.height is not None else settings.WALL_HEIGHT
        texture_name = seg.texture_name
        if texture_name:
            texture_id = self.texture_manager.get_gl_texture_id(texture_name)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glColor3f(1, 1, 1)

            glBegin(GL_QUADS)

            # Escala de textura
            tex_scale = (
                settings.TEXTURE_SCALE if hasattr(settings, "TEXTURE_SCALE") else 1.0
            )

            # Longitud total del segmento original
            total_length = (
                seg.original_segment.length() if seg.original_segment else seg.length()
            )

            # Calcular UVs en base a la escala y el offset global
            u_start = (seg.u_offset / tex_scale) if total_length > 0 else 0
            u_end = (
                ((seg.u_offset + seg.length()) / tex_scale) if total_length > 0 else 1
            )

            glTexCoord2f(u_start, 0)
            glVertex3f(seg.a.x, 0, seg.a.y)

            glTexCoord2f(u_end, 0)
            glVertex3f(seg.b.x, 0, seg.b.y)

            glTexCoord2f(u_end, 1)
            glVertex3f(seg.b.x, h, seg.b.y)

            glTexCoord2f(u_start, 1)
            glVertex3f(seg.a.x, h, seg.a.y)

            glEnd()
            glDisable(GL_TEXTURE_2D)
        else:
            color = self.theme.get("wall_interior", (255, 255, 255))
            dim_factor = 0.8
            glColor3f(
                color[0] / 255.0 * dim_factor,
                color[1] / 255.0 * dim_factor,
                color[2] / 255.0 * dim_factor,
            )

            glBegin(GL_QUADS)
            # Vertices en el plano XZ, altura en Y
            # Abajo-Izquierda
            glVertex3f(seg.a.x, 0, seg.a.y)
            # Abajo-Derecha
            glVertex3f(seg.b.x, 0, seg.b.y)
            # Arriba-Derecha
            glVertex3f(seg.b.x, h, seg.b.y)
            # Arriba-Izquierda
            glVertex3f(seg.a.x, h, seg.a.y)
            glEnd()

    def _draw_3d_wall(self, seg: Segment) -> None:
        glUseProgram(self.shader_program)
        h = seg.height if seg.height is not None else settings.WALL_HEIGHT

        # Coordenadas de textura (UV)
        # u_start, u_end = 0.0, 1.0  # Calcula según tu lógica de textura

        # Escala de textura
        tex_scale = (
            settings.TEXTURE_SCALE if hasattr(settings, "TEXTURE_SCALE") else 1.0
        )

        # Longitud total del segmento original
        total_length = (
            seg.original_segment.length() if seg.original_segment else seg.length()
        )

        # Calcular UVs en base a la escala y el offset global
        u_start = (seg.u_offset / tex_scale) if total_length > 0 else 0
        u_end = ((seg.u_offset + seg.length()) / tex_scale) if total_length > 0 else 1

        vertices = np.array(
            [
                [seg.a.x, 0, seg.a.y, u_start, 0],
                [seg.b.x, 0, seg.b.y, u_end, 0],
                [seg.b.x, h, seg.b.y, u_end, 1],
                [seg.a.x, h, seg.a.y, u_start, 1],
            ],
            dtype=np.float32,
        )

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        pos_loc = glGetAttribLocation(self.shader_program, "position")
        uv_loc = glGetAttribLocation(self.shader_program, "texCoordIn")
        glEnableVertexAttribArray(pos_loc)
        glVertexAttribPointer(pos_loc, 3, GL_FLOAT, False, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(uv_loc)
        glVertexAttribPointer(uv_loc, 2, GL_FLOAT, False, 20, ctypes.c_void_p(12))

        # Enlazar textura si existe
        if seg.texture_name:
            texture_id = self.texture_manager.get_gl_texture_id(seg.texture_name)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            tex_loc = glGetUniformLocation(self.shader_program, "wallTexture")
            glUniform1i(tex_loc, 0)

        # --- Enviar matrices modelview y projection ---
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        projection = glGetFloatv(GL_PROJECTION_MATRIX)
        mv_loc = glGetUniformLocation(self.shader_program, "modelview")
        pr_loc = glGetUniformLocation(self.shader_program, "projection")
        glUniformMatrix4fv(mv_loc, 1, GL_FALSE, modelview)
        glUniformMatrix4fv(pr_loc, 1, GL_FALSE, projection)

        glDrawArrays(GL_QUADS, 0, 4)
        glDisableVertexAttribArray(pos_loc)
        glDisableVertexAttribArray(uv_loc)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDeleteBuffers(1, [vbo])
        glUseProgram(0)

    def _draw_grid(self) -> None:
        """Dibuja una grilla en el plano XZ."""
        grid_color = colors.GRAY  # Usar el color gris definido
        glColor3f(grid_color[0] / 255.0, grid_color[1] / 255.0, grid_color[2] / 255.0)
        glLineWidth(1.2)  # Grosor de las líneas de la grilla
        grid_size = 50  # Espaciado entre líneas de la grilla
        max_grid = 1000  # Extensión de la grilla

        glBegin(GL_LINES)
        for i in range(-max_grid, max_grid + grid_size, grid_size):
            # Líneas verticales (eje X)
            glVertex3f(i, 0, -max_grid)
            glVertex3f(i, 0, max_grid)

            # Líneas horizontales (eje Z)
            glVertex3f(-max_grid, 0, i)
            glVertex3f(max_grid, 0, i)
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

        # Deshabilitar el test de profundidad
        glDisable(GL_DEPTH_TEST)

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

    # Métodos de dibujo internos (usando OpenGL)

    def _draw_map(
        self, map_data: MapData, visible_segments: Optional[Iterable[Segment]]
    ) -> None:
        for seg in map_data.segments:
            self._draw_segment(seg, is_visible=False)
        if visible_segments is not None:
            for seg in visible_segments:
                self._draw_segment(seg, is_visible=True)

    def _draw_segment(self, seg: Segment, is_visible: bool) -> None:
        """
        Dibuja un segmento en el minimapa y su normal como una pequeña línea.
        """
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

        # --- Dibuja la normal de la pared como una línea corta ---
        # Calcula el punto medio del segmento
        mx = (seg.a.x + seg.b.x) / 2
        my = (seg.a.y + seg.b.y) / 2
        # Calcula la dirección normal (perpendicular)
        dx = seg.b.x - seg.a.x
        dy = seg.b.y - seg.a.y
        length = (dx**2 + dy**2) ** 0.5
        if length > 0:
            # Normalizada y perpendicular (rotar 90 grados)
            nx = -dy / length
            ny = dx / length
            # Longitud de la línea de la normal
            normal_len = 12.0
            # Color para la normal (cyan)
            glColor3f(0, 1, 1)
            glLineWidth(2.0)
            glBegin(GL_LINES)
            glVertex2f(mx, my)
            glVertex2f(mx + nx * normal_len, my + ny * normal_len)
            glEnd()
        # ...existing code...

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

    # Menu

    def draw_main_menu(self, options, selected_index):
        from OpenGL.GL import (
            glClear,
            glClearColor,
            glColor3f,
            glBegin,
            glEnd,
            glVertex2f,
            GL_COLOR_BUFFER_BIT,
            GL_QUADS,
        )

        width, height = self.width, self.height
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Parámetros de los botones
        btn_w, btn_h = 300, 60
        spacing = 40
        start_y = height // 2 + btn_h

        for i, opt in enumerate(options):
            x = (width - btn_w) // 2
            y = start_y - i * (btn_h + spacing)
            if i == selected_index:
                glColor3f(1.0, 1.0, 1.0)  # Blanco
            else:
                glColor3f(0.5, 0.5, 0.5)  # Gris

            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + btn_w, y)
            glVertex2f(x + btn_w, y - btn_h)
            glVertex2f(x, y - btn_h)
            glEnd()
