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
import ctypes

import logging

logger = logging.getLogger(__name__)


class WorldRenderer:
    def __init__(self, renderer):
        self.renderer = renderer  # Referencia al GLFWOpenGLRenderer
        self.theme = renderer.theme

    def draw_3d_world(
        self, player: Player, visible_segments: list[Segment], map_data: MapData
    ):
        """
        Renderiza el mundo 3D usando los segmentos visibles completos.
        Además, dibuja las caras del suelo de cada polígono del mapa.
        """

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        # Configura proyección 3D
        self._setup_3d_projection(player)

        # Configurar Cámara
        glMatrixMode(GL_MODELVIEW)
        glDepthFunc(GL_LESS)
        glLoadIdentity()

        glRotatef(player.angle_deg + 90, 0.0, 1.0, 0.0)
        glTranslatef(-player.x, -settings.PLAYER_HEIGHT, -player.y)

        # --- Renderizado del mundo ---
        # 1. Dibujar el suelo de los polígonos visibles
        self._draw_floors(map_data, visible_segments)

        # 2. Dibujar las paredes visibles
        if visible_segments:
            for seg in visible_segments:
                self._draw_3d_wall(seg, player)

        # 3. Dibujar grilla (opcional, puedes comentarla para ver mejor el suelo)
        # self._draw_grid()

    def draw_2d_minimap(self, map_data: MapData, player: Player, visible_segments):
        """
        Renderiza el minimapa usando los segmentos visibles completos.
        La lista visible_segments debe ser generada por VisibilityManager.
        """

        # Desactivar pruebas de profundidad y culling
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        # Configurar proyección 2D
        self._setup_2d_projection()

        # Configurar matrix de vista
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Camara 2D
        self.renderer.camera.set_target(player.x, player.y)
        self.renderer.camera.apply_transform()

        # Dibujar el mapa
        self._draw_map(map_data, visible_segments)
        self._draw_player(player)

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

    def _draw_floors(self, map_data: MapData, visible_segments: list[Segment]):
        """
        Dibuja el suelo de los polígonos visibles usando shaders.
        Puede usar una textura si está definida, o un color sólido como fallback.
        """
        shader = self.renderer.floor_shader_program
        if not shader or not visible_segments or not map_data.polygons:
            return

        glUseProgram(shader)

        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        projection = glGetFloatv(GL_PROJECTION_MATRIX)
        glUniformMatrix4fv(
            glGetUniformLocation(shader, "modelview"), 1, GL_FALSE, modelview
        )
        glUniformMatrix4fv(
            glGetUniformLocation(shader, "projection"), 1, GL_FALSE, projection
        )

        use_texture_loc = glGetUniformLocation(shader, "useTexture")
        color_loc = glGetUniformLocation(shader, "floorColor")
        texture_sampler_loc = glGetUniformLocation(shader, "floorTexture")

        tex_scale = (
            settings.TEXTURE_SCALE if hasattr(settings, "TEXTURE_SCALE") else 1.0
        )

        drawn_polygons = set()
        for seg in visible_segments:
            if seg.polygon_name and seg.polygon_name not in drawn_polygons:
                drawn_polygons.add(seg.polygon_name)
                poly_vertices = map_data.polygons.get(seg.polygon_name)

                if not poly_vertices or len(poly_vertices) < 3:
                    continue

                # --- Configuración por polígono (textura o color) ---
                use_texture = (
                    seg.texture_name and seg.texture_name != "floor_placeholder"
                )
                glUniform1i(use_texture_loc, GL_TRUE if use_texture else GL_FALSE)

                if use_texture:
                    texture_id = self.renderer.texture_manager.get_gl_texture_id(
                        seg.texture_name
                    )
                    glActiveTexture(GL_TEXTURE0)
                    glBindTexture(GL_TEXTURE_2D, texture_id)
                    glUniform1i(texture_sampler_loc, 0)
                else:
                    floor_color_rgb = self.theme.get("floor", colors.DARK_GRAY)
                    floor_color_gl = [c / 255.0 for c in floor_color_rgb]
                    glUniform3f(color_loc, *floor_color_gl)

                # --- Preparación de Vértices (Posición + UVs) ---
                vertex_data = []
                # --- CAMBIO CLAVE: Iteramos sobre los vértices en orden INVERSO ---
                for v in reversed(poly_vertices):
                    vertex_data.extend(
                        [
                            v.x,
                            0.0,
                            v.y,  # position (x, 0, z)
                            v.x / tex_scale,
                            v.y / tex_scale,  # texCoord (u, v)
                        ]
                    )
                vertices = np.array(vertex_data, dtype=np.float32)

                # --- Creación de VBO y dibujado ---
                vbo = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, vbo)
                glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

                pos_loc = glGetAttribLocation(shader, "position")
                glEnableVertexAttribArray(pos_loc)
                glVertexAttribPointer(
                    pos_loc, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0)
                )

                uv_loc = glGetAttribLocation(shader, "texCoordIn")
                glEnableVertexAttribArray(uv_loc)
                glVertexAttribPointer(
                    uv_loc, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12)
                )

                glDrawArrays(GL_TRIANGLE_FAN, 0, len(poly_vertices))

                glDisableVertexAttribArray(pos_loc)
                glDisableVertexAttribArray(uv_loc)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glDeleteBuffers(1, [vbo])

        glUseProgram(0)

        """
        if not visible_segments or not map_data.polygons:
            return

        floor_color = self.theme.get("floor", colors.DARK_GRAY)
        glColor3f(
            floor_color[0] / 255.0, floor_color[1] / 255.0, floor_color[2] / 255.0
        )

        # Desactivamos los shaders para dibujar con color fijo (modo inmediato)
        glUseProgram(0)

        # Usamos un set para no dibujar el mismo polígono varias veces
        drawn_polygons = set()

        for seg in visible_segments:
            # Si el segmento pertenece a un polígono y no lo hemos dibujado ya
            # logger.debug(" Polígono: %s", seg.polygon_name)

            if seg.polygon_name and seg.polygon_name not in drawn_polygons:
                # Lo marcamos como dibujado
                drawn_polygons.add(seg.polygon_name)

                # Obtenemos sus vértices desde map_data
                poly_vertices = map_data.polygons.get(seg.polygon_name)
                logger.debug(
                    " Dibujando polígono: %s con vértices %s",
                    seg.polygon_name,
                    poly_vertices,
                )
                if poly_vertices:
                    glBegin(GL_POLYGON)
                    for vertex in poly_vertices:
                        # Dibujamos el polígono en el plano Y=0
                        glVertex3f(vertex.x, 0, vertex.y)
                    glEnd()
        """

    def _draw_3d_wall(self, seg: Segment, player: Player):
        shader = self.renderer.shader_program
        if not shader:
            return
        glUseProgram(shader)

        h = seg.height if seg.height is not None else settings.WALL_HEIGHT

        tex_scale = (
            settings.TEXTURE_SCALE if hasattr(settings, "TEXTURE_SCALE") else 1.0
        )

        u_start = seg.u_offset / tex_scale
        u_end = (seg.u_offset + seg.length()) / tex_scale

        # Definimos los puntos de inicio y fin del segmento de la pared.
        # Dependiendo de la orientación de la cara, los usaremos en un orden u otro.
        v_start = seg.a
        v_end = seg.b

        if seg.interior_facing:
            # La cara visible es la interior. El orden CCW visto desde dentro es:
            # start -> end -> end_top -> start_top
            # Esto corresponde a los vértices (a, b, b_top, a_top)
            p1, p2 = v_start, v_end
            uv1, uv2 = u_start, u_end

        else:
            # La cara visible es la exterior. El orden CCW visto desde fuera es:
            # end -> start -> start_top -> end_top
            # Esto corresponde a los vértices (b, a, a_top, b_top)
            p1, p2 = v_end, v_start
            uv1, uv2 = u_end, u_start

        p1, p2 = v_start, v_end
        uv1, uv2 = u_start, u_end

        vertices = np.array(
            [
                # Vértices definidos dinámicamente para ser siempre CCW en la cara visible
                [p1.x, 0, p1.y, uv1, 0],  # Abajo-Izquierda
                [p2.x, 0, p2.y, uv2, 0],  # Abajo-Derecha
                [p2.x, h, p2.y, uv2, 1],  # Arriba-Derecha
                [p1.x, h, p1.y, uv1, 1],  # Arriba-Izquierda
            ],
            dtype=np.float32,
        )

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        pos_loc = glGetAttribLocation(shader, "position")
        uv_loc = glGetAttribLocation(shader, "texCoordIn")
        glEnableVertexAttribArray(pos_loc)
        glVertexAttribPointer(pos_loc, 3, GL_FLOAT, False, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(uv_loc)
        glVertexAttribPointer(uv_loc, 2, GL_FLOAT, False, 20, ctypes.c_void_p(12))

        if seg.texture_name:
            texture_id = self.renderer.texture_manager.get_gl_texture_id(
                seg.texture_name
            )
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            tex_loc = glGetUniformLocation(shader, "wallTexture")
            glUniform1i(tex_loc, 0)

        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        projection = glGetFloatv(GL_PROJECTION_MATRIX)
        mv_loc = glGetUniformLocation(shader, "modelview")
        pr_loc = glGetUniformLocation(shader, "projection")
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
        grid_color = colors.GRAY
        glColor3f(grid_color[0] / 255.0, grid_color[1] / 255.0, grid_color[2] / 255.0)
        glLineWidth(1.5)
        grid_size = 50
        max_grid = 1000

        glBegin(GL_LINES)
        for i in range(-max_grid, max_grid + grid_size, grid_size):
            glVertex3f(i, 0, -max_grid)
            glVertex3f(i, 0, max_grid)
            glVertex3f(-max_grid, 0, i)
            glVertex3f(max_grid, 0, i)
        glEnd()

    def _draw_map(self, map_data, visible_segments):
        for seg in map_data.segments:
            self._draw_segment(seg, is_visible=False)
        if visible_segments is not None:
            for seg in visible_segments:
                self._draw_segment(seg, is_visible=True)

    def _draw_segment(self, seg, is_visible=False):
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

        glBegin(GL_LINES)
        for i in range(20):
            angle1 = (i / 20) * 2 * math.pi
            angle2 = ((i + 1) / 20) * 2 * math.pi
            glVertex2f(px + math.cos(angle1) * 4, py + math.sin(angle1) * 4)
            glVertex2f(px + math.cos(angle2) * 4, py + math.sin(angle2) * 4)
        glEnd()

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
