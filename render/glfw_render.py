"""
render/glfw_render.py
Renderizador que utiliza GLFW para la ventana y PyOpenGL para el renderizado 2D del minimapa.
"""

from __future__ import annotations
import logging
import math
import numpy as np
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
    GL_STENCIL_BUFFER_BIT,
    GL_PROJECTION,
    GL_MODELVIEW,
    GL_LINES,
    GL_QUADS,
    glGetString,
    GL_VERSION,
    GL_DEPTH_TEST,
    glEnable,
    glDisable,
    glBindTexture,
    glTexCoord2f,
    GL_TEXTURE_2D,
    shaders,
    GL_VERTEX_SHADER,
    GL_FRAGMENT_SHADER,
    glUseProgram,
    glGetAttribLocation,
    glEnableVertexAttribArray,
    glVertexAttribPointer,
    glGetUniformLocation,
    glUniform3f,
    glUniformMatrix4fv,
    glGenBuffers,
    glBindBuffer,
    glBufferData,
    glDrawArrays,
    glDisableVertexAttribArray,
    glDeleteBuffers,
    GL_ARRAY_BUFFER,
    GL_FLOAT,
    GL_QUADS,
    GL_STATIC_DRAW,
    glGetFloatv,
    GL_MODELVIEW_MATRIX,
    GL_PROJECTION_MATRIX,
    GL_FALSE,
    glRotatef,
    glOrtho,
    glViewport,
    glMatrixMode,
)

from core.texture_manager import TextureManager
from .glfw_camera import Camera2D
from .world_renderer import WorldRenderer
from .ui_renderer import UIRenderer
from .renderer_base import IRenderer
from core.map_data import MapData
from core.player import Player
import settings
from core.types import Segment, Vec2
from . import colors


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
        if not vertex_src or not fragment_src:
            raise RuntimeError("No se pudieron cargar los shaders")
        logger.info("Compilando shaders OpenGL...")
        try:
            self.shader_program = shaders.compileProgram(
                shaders.compileShader(vertex_src, GL_VERTEX_SHADER),
                shaders.compileShader(fragment_src, GL_FRAGMENT_SHADER),
            )
        except Exception as e:
            logger.error("Error al compilar los shaders: %s", e)
            raise RuntimeError("Fallo al compilar los shaders OpenGL") from e

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

        self.theme = color_theme if color_theme is not None else colors.default_theme()
        self.world_renderer = WorldRenderer(self)
        self.texture_manager = TextureManager()

        self.width = width
        self.height = height

        self.window = glfw.create_window(width, height, caption, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Fallo al crear la ventana GLFW")

        glfw.make_context_current(self.window)
        glEnable(GL_DEPTH_TEST)

        self._init_shaders()

        try:
            self.gl_version = glGetString(GL_VERSION).decode()
        except Exception as e:
            self.gl_version = "Unknown"

        glfw.set_window_size_callback(self.window, self._on_resize)
        self.world_renderer = WorldRenderer(self)
        self.camera = Camera2D(width=width, height=height, scale=scale)
        self._setup_gl(width, height)

    def get_opengl_version(self) -> str:
        """Devuelve la version de OpenGL utilizada."""
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

        self.world_renderer.draw_3d_world(player, visible_segments)
        self.world_renderer.draw_2d_minimap(map_data, player, visible_segments)

    def dispatch_events(self) -> None:
        glfw.poll_events()

    def flip_buffers(self) -> None:
        glfw.swap_buffers(self.window)

    def shutdown(self) -> None:
        logger.info("Cerrando GLFW.")
        glfw.terminate()

    def draw_main_menu(self, options, selected_index):
        """
        Dibuja el menú principal usando UIRenderer.
        """
        if not hasattr(self, "ui_renderer"):
            self.ui_renderer = UIRenderer(self)
        self.ui_renderer.draw_main_menu(options, selected_index)
