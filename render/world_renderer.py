"""
WorldRenderer: Clase encargada de renderizar el mundo en 3D y el minimapa en 2D.
"""

from core.player import Player
from core.map_data import MapData
from core.types import Segment
from render import colors
import settings

from OpenGL.GL import *
from OpenGL.GLU import gluPerspective

import math
import numpy as np


class WorldRenderer:
    def __init__(self, renderer):
        self.renderer = renderer  # Referencia al GLFWOpenGLRenderer
        self.theme = renderer.theme

    def draw_3d_world(self, player: Player, visible_segments):
        # Configura proyección 3D y dibuja paredes
        self._setup_3d_projection(player)
        # Configurar Camara
        glMatrixMode(GL_MODELVIEW)
        # glDepthFunc(GL_LESS)
        glLoadIdentity()

        glRotatef(player.angle_deg + 90, 0.0, 1.0, 0.0)
        glTranslatef(-player.x, -settings.PLAYER_HEIGHT, -player.y)

        # Dibujar las paredes visibles
        if visible_segments:
            for seg in visible_segments:
                self._draw_3d_wall(seg, player)

        # Dibujar grilla
        self._draw_grid()

    def draw_2d_minimap(self, map_data: MapData, player: Player, visible_segments):
        # Configura proyección 2D y dibuja minimapa
        self._setup_2d_projection()
        glDisable(GL_DEPTH_TEST)

        # Configurar matrix de vista
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Camara 2D
        self.renderer.camera.set_target(player.x, player.y)
        self.renderer.camera.apply_transform()

        # Dibujar el mapa
        self._draw_map(map_data, visible_segments)
        self._draw_player(player)

        # Rehabilitar el test de profundidad
        glEnable(GL_DEPTH_TEST)

    def _setup_3d_projection(self, player: Player) -> None:
        """
        Configura la mastriz para la vista del jugador en 3D.
        """

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        width = self.renderer.width
        height = self.renderer.height
        aspect_ratio = width / height if height > 0 else 1.0

        horizontal_fov_rad = math.radians(player.fov_deg)
        vertical_fov_rad = 2 * math.atan(
            math.tan(horizontal_fov_rad / 2) / aspect_ratio
        )
        vertical_fov_deg = math.degrees(vertical_fov_rad)

        gluPerspective(vertical_fov_deg, aspect_ratio, 0.1, 2000.0)

    def _setup_2d_projection(self):
        """
        Configura la matriz para la vista 2D
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        width = self.renderer.width
        height = self.renderer.height
        glOrtho(0, width, 0, height, -1, 1)

    def _draw_3d_wall(self, seg: Segment, player: Player):
        glUseProgram(self.renderer.shader_program)
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

        pos_loc = glGetAttribLocation(self.renderer.shader_program, "position")
        uv_loc = glGetAttribLocation(self.renderer.shader_program, "texCoordIn")
        glEnableVertexAttribArray(pos_loc)
        glVertexAttribPointer(pos_loc, 3, GL_FLOAT, False, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(uv_loc)
        glVertexAttribPointer(uv_loc, 2, GL_FLOAT, False, 20, ctypes.c_void_p(12))

        # Enlazar textura si existe
        if seg.texture_name:
            texture_id = self.renderer.texture_manager.get_gl_texture_id(
                seg.texture_name
            )
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            tex_loc = glGetUniformLocation(self.renderer.shader_program, "wallTexture")
            glUniform1i(tex_loc, 0)

        # --- Enviar matrices modelview y projection ---
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        projection = glGetFloatv(GL_PROJECTION_MATRIX)
        mv_loc = glGetUniformLocation(self.renderer.shader_program, "modelview")
        pr_loc = glGetUniformLocation(self.renderer.shader_program, "projection")
        glUniformMatrix4fv(mv_loc, 1, GL_FALSE, modelview)
        glUniformMatrix4fv(pr_loc, 1, GL_FALSE, projection)

        glDrawArrays(GL_QUADS, 0, 4)
        glDisableVertexAttribArray(pos_loc)
        glDisableVertexAttribArray(uv_loc)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDeleteBuffers(1, [vbo])
        glUseProgram(0)

    def _draw_grid(self):
        """Dibuja una grilla en el plano XZ."""
        grid_color = colors.GRAY  # Usar el color gris definido
        glColor3f(grid_color[0] / 255.0, grid_color[1] / 255.0, grid_color[2] / 255.0)
        glLineWidth(1.5)  # Grosor de las líneas de la grilla
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

    def _draw_map(self, map_data, visible_segments):
        # Dibuja los segmentos del mapa y los visibles
        for seg in map_data.segments:
            self._draw_segment(seg, is_visible=False)
        if visible_segments is not None:
            for seg in visible_segments:
                self._draw_segment(seg, is_visible=True)

    def _draw_segment(self, seg, is_visible=False):
        # Selecciona el color según si el segmento es visible
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

    def _draw_player(self, player: Player):
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
