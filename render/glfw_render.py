"""
GLFW_OpenGLRenderer: Control de renderizado usando GLFW y OpenGL.
Esta clase gestiona la ventana, el contexto OpenGL y el renderizado del mundo 3D y UI.
"""

from __future__ import annotations
import logging
from typing import Dict, Any, Iterable, Optional

import glfw
from OpenGL.GL import *
from OpenGL.GL import shaders
from core.texture_manager import TextureManager
from .glfw_camera import Camera2D, MainCamera, HUDCamera
from .world_renderer import WorldRenderer
from .ui_renderer import UIRenderer
from .renderer_base import IRenderer
from .ui_label import UILabel
from core.map_data import MapData
from core.player import Player
import settings
from core._types import Segment
from . import colors
from core.visibility import VisibilityManager
from render.glsl_lights import PointLight, GlobalLight


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

    def _compile_shader_program(self, vert_path: str, frag_path: str) -> int:
        """Compila un par de shaders y devuelve el ID del programa."""
        try:
            vertex_src = load_shader_source(vert_path)
            fragment_src = load_shader_source(frag_path)
            if not vertex_src or not fragment_src:
                raise RuntimeError(
                    f"No se pudieron cargar los shaders: {vert_path}, {frag_path}"
                )

            program = shaders.compileProgram(
                shaders.compileShader(vertex_src, GL_VERTEX_SHADER),
                shaders.compileShader(fragment_src, GL_FRAGMENT_SHADER),
            )
            return program
        except Exception as e:
            logger.error(
                "Error al compilar shaders (%s, %s): %s", vert_path, frag_path, e
            )
            raise RuntimeError("Fallo al compilar los shaders OpenGL") from e

    def _init_shaders(self):
        """
        Inicializa todos los programas de shaders necesarios de forma eficiente y extensible.
        Utiliza una lista de definiciones para evitar repetición y facilitar la extensión.
        """
        # Definición de los shaders a compilar: (atributo, vert_path, frag_path, descripción)
        shader_defs = [
            (
                "shader_program",
                "assets/shaders/wall.vert",
                "assets/shaders/wall.frag",
                "pared",
            ),
            (
                "floor_shader_program",
                "assets/shaders/floor.vert",
                "assets/shaders/floor.frag",
                "suelo",
            ),
            (
                "ceiling_shader_program",
                "assets/shaders/ceiling.vert",
                "assets/shaders/ceiling.frag",
                "techo",
            ),
            (
                "ui_button_shader_program",
                "assets/shaders/ui_button.vert",
                "assets/shaders/ui_button.frag",
                "UI_button",
            ),
            (
                "ui_label_shader_program",
                "assets/shaders/ui_label.vert",
                "assets/shaders/ui_label.frag",
                "UI_label",
            ),
        ]

        for attr, vert, frag, desc in shader_defs:
            try:
                logger.info(f"Compilando shaders de {desc}...")
                program = self._compile_shader_program(vert, frag)
                setattr(self, attr, program)
            except Exception as e:
                logger.error(f"Error al compilar shaders de {desc}: {e}")
                setattr(self, attr, None)

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

        self.theme = color_theme if color_theme is not None else colors.default_theme()
        self.texture_manager = TextureManager()
        self.shader_program = None
        self.floor_shader_program = None
        self.ceiling_shader_program = None
        self.ui_shader_program = None

        self.width = width
        self.height = height

        self.window = glfw.create_window(width, height, caption, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Fallo al crear la ventana GLFW")

        glfw.make_context_current(self.window)
        # El estado por defecto al inicio de un frame será para 3D
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        self._init_shaders()

        try:
            self.gl_version = glGetString(GL_VERSION).decode()
        except Exception as e:
            self.gl_version = "Unknown"

        glfw.set_window_size_callback(self.window, self._on_resize)
        self.world_renderer = WorldRenderer(self)
        self.camera = Camera2D(width=width, height=height, scale=scale)
        self.main_camera = MainCamera()
        self.hud_camera = HUDCamera(width=width, height=height)
        self._setup_gl(width, height)

        self.point_light = PointLight(
            position=(-140.0, 20.0, 95.0),
            color=(1.0, 1.0, 1.0),
            intensity=30.0,
            range=150.0,
        )  # Luz puntual roja en la esquina (0,0)
        self.global_light = GlobalLight(
            color=(1.0, 1.0, 1.0), intensity=0.1
        )  # Luz global blanca suave

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
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        self.camera.update_viewport(width, height)
        self.hud_camera.update_viewport(width, height)

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
        Actualiza la posición de la luz puntual para que siga al jugador antes de renderizar.
        """
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # --- Actualizar la posición de la luz puntual para que siga al jugador ---
        self.point_light.set(position=(0, 0, 0))

        # --- Sincronizar la cámara principal con el jugador ---
        self.main_camera.follow_player(player)

        if (
            visible_segments is None
            and hasattr(map_data, "bsp_root")
            and map_data.bsp_root
        ):
            visible_segments = VisibilityManager.compute_visible_segments(
                map_data.bsp_root, player
            )

        # --- Renderizado del mundo y minimapa ---
        self.world_renderer.draw_3d_world(self.main_camera, visible_segments, map_data)
        self.world_renderer.draw_2d_minimap(map_data, player, visible_segments)

        # --- HUD: Mostrar la posición del jugador usando HUDCamera y UILabel ---
        self.hud_camera.apply_transform()
        if not hasattr(self, "ui_renderer"):
            self.ui_renderer = UIRenderer(self)
        # Crear etiqueta HUD y dibujarla

        label = UILabel(
            text=f"Pos: x={player.x:.1f} y={player.y:.1f} z={getattr(player, 'z', 0.0):.1f}",
            x=12,  # self.width - 420,
            y=12,
            color=(255, 255, 255, 255),
            bg_color=(0, 0, 0, 180),
            font_size=16,
        )
        self.ui_renderer.draw_label(label, self.width, self.height)

    def dispatch_events(self) -> None:
        glfw.poll_events()

    def flip_buffers(self) -> None:
        glfw.swap_buffers(self.window)

    def shutdown(self) -> None:
        logger.info("Cerrando GLFW.")
        if self.shader_program:
            glDeleteProgram(self.shader_program)
        if self.floor_shader_program:
            glDeleteProgram(self.floor_shader_program)
        if self.ceiling_shader_program:
            glDeleteProgram(self.ceiling_shader_program)
        if self.ui_shader_program:
            glDeleteProgram(self.ui_shader_program)

        if hasattr(self, "ui_renderer"):
            self.ui_renderer.cleanup()

        glfw.terminate()

    def draw_main_menu(self, options, selected_index):
        """
        Dibuja el menú principal usando UIRenderer.
        """
        if not hasattr(self, "ui_renderer"):
            self.ui_renderer = UIRenderer(self)
        self.ui_renderer.draw_main_menu(options, selected_index)

    # No se requieren cambios aquí, la lógica de sincronización de FOV y proyección está centralizada en MainCamera y WorldRenderer.
