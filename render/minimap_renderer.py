import os
import numpy as np
from OpenGL.GL import *

import logging

logger = logging.getLogger(__name__)


class MinimapRenderer:
    """
    Renderiza el minimapa usando un shader dedicado.
    Se encarga de cargar los shaders, la textura del mapa y dibujar el minimapa en la UI.
    """

    def __init__(self, shader_dir="assets/shaders/"):
        # Cargar y compilar shaders
        self.shader_program = self._load_shaders(
            os.path.join(shader_dir, "minimap.vert"),
            os.path.join(shader_dir, "minimap.frag"),
        )
        # Crear quad para el minimapa (dos triángulos)
        self.vao, self.vbo = self._create_quad()
        self.map_texture = None
        self.player_pos = (0.5, 0.5)
        self.player_radius = 0.03

    def set_map_texture(self, texture_id):
        """Asigna la textura del mapa a mostrar en el minimapa."""
        self.map_texture = texture_id

    def set_player_position(self, x, y):
        """Actualiza la posición del jugador en el minimapa (valores normalizados [0,1])."""
        self.player_pos = (x, y)

    def render(self):
        """Dibuja el minimapa en la pantalla."""
        if self.map_texture is None:
            # logger.warning("No se ha asignado textura de minimapa.")
            return

        glUseProgram(self.shader_program)
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.map_texture)
        glUniform1i(glGetUniformLocation(self.shader_program, "uMapTexture"), 0)
        glUniform2f(
            glGetUniformLocation(self.shader_program, "uPlayerPos"), *self.player_pos
        )
        glUniform1f(
            glGetUniformLocation(self.shader_program, "uPlayerRadius"),
            self.player_radius,
        )
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glBindVertexArray(0)
        glUseProgram(0)

    def _load_shaders(self, vert_path, frag_path):
        """Carga y compila los shaders desde archivos."""
        with open(vert_path, "r") as f:
            vert_src = f.read()
        with open(frag_path, "r") as f:
            frag_src = f.read()
        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vert_shader, vert_src)
        glCompileShader(vert_shader)
        if not glGetShaderiv(vert_shader, GL_COMPILE_STATUS):
            raise RuntimeError(glGetShaderInfoLog(vert_shader).decode())
        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(frag_shader, frag_src)
        glCompileShader(frag_shader)
        if not glGetShaderiv(frag_shader, GL_COMPILE_STATUS):
            raise RuntimeError(glGetShaderInfoLog(frag_shader).decode())
        program = glCreateProgram()
        glAttachShader(program, vert_shader)
        glAttachShader(program, frag_shader)
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(program).decode())
        glDeleteShader(vert_shader)
        glDeleteShader(frag_shader)
        return program

    def _create_quad(self):
        """Crea un quad de pantalla completa para el minimapa."""
        # Posiciones y coordenadas de textura (X, Y, U, V)
        quad = np.array(
            [
                -0.8,
                -0.8,
                0.0,
                0.0,
                -0.4,
                -0.8,
                1.0,
                0.0,
                -0.8,
                -0.4,
                0.0,
                1.0,
                -0.4,
                -0.4,
                1.0,
                1.0,
            ],
            dtype=np.float32,
        )
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, quad.nbytes, quad, GL_STATIC_DRAW)
        # Posición
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 4 * quad.itemsize, ctypes.c_void_p(0)
        )
        glEnableVertexAttribArray(0)
        # TexCoord
        glVertexAttribPointer(
            1,
            2,
            GL_FLOAT,
            GL_FALSE,
            4 * quad.itemsize,
            ctypes.c_void_p(2 * quad.itemsize),
        )
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        return vao, vbo
