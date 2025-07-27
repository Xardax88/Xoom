"""
WorldRenderer: Clase encargada de renderizar el mundo en 3D y el minimapa en 2D.
"""

from core.player import Player
from core.map_data import MapData
from core._types import Segment
from render import colors
from render.glsl_models import (
    WallModel,
    FloorModel,
    CeilingModel,
)  # <--- Importar modelos GLSL
import settings

from OpenGL.GL import *
from OpenGL.GLU import gluPerspective

import math
import numpy as np

import logging

logger = logging.getLogger(__name__)


class WorldRenderer:
    def __init__(self, renderer):
        self.renderer = renderer  # Referencia al GLFWOpenGLRenderer
        self.theme = renderer.theme

    def draw_3d_world(self, camera, visible_segments: list[Segment], map_data: MapData):
        """
        Renderiza el mundo 3D usando los segmentos visibles completos.
        Utiliza la posición y ángulo de la cámara principal (no del jugador).
        """
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        self._setup_3d_projection(camera)

        glMatrixMode(GL_MODELVIEW)
        glDepthFunc(GL_LESS)
        glLoadIdentity()

        # Usar la posición y ángulo de la cámara principal
        glRotatef(camera.angle_deg + 90, 0.0, 1.0, 0.0)
        glTranslatef(-camera.x, -settings.PLAYER_HEIGHT, -camera.z)

        # --- Renderizado del mundo ---
        # Dibujar el suelo de los polígonos visibles
        self._draw_floors(map_data, visible_segments)
        self._draw_ceilings(map_data, visible_segments)

        # Dibujar las paredes visibles, asegurando que cada segmento se dibuje solo una vez
        drawn_segments = set()
        if visible_segments:
            for seg in visible_segments:
                # Crea una clave única para cada segmento usando sus extremos y polígono
                seg_key = (
                    round(seg.a.x, 5),
                    round(seg.a.y, 5),
                    round(seg.b.x, 5),
                    round(seg.b.y, 5),
                    seg.polygon_name,
                )
                if seg_key in drawn_segments:
                    continue
                drawn_segments.add(seg_key)
                self._draw_3d_wall(seg, camera)

        # Dibujar grilla
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

    def _setup_3d_projection(self, camera) -> None:
        """
        Configura la matriz para la vista de la cámara principal en 3D.
        El FOV horizontal se toma directamente del atributo fov_deg de la cámara,
        que debe estar sincronizado con el jugador para evitar desincronización visual.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        width = self.renderer.width
        height = self.renderer.height
        aspect_ratio = width / height if height > 0 else 1.0

        # Usar SIEMPRE el FOV de la cámara (ya sincronizado con el jugador)
        horizontal_fov_deg = getattr(camera, "fov_deg", 90.0)
        horizontal_fov_rad = math.radians(horizontal_fov_deg)
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
        Dibuja el suelo de todos los polígonos principales (sectores) usando shaders.
        El suelo se dibuja a la altura floor_h de cada sector.
        """
        shader = self.renderer.floor_shader_program
        if not shader or not map_data.polygons:
            return

        glUseProgram(shader)

        # Enviar uniforms de iluminación dinámica (luz puntual y global)
        self.renderer.point_light.set_uniforms(shader)
        self.renderer.global_light.set_uniforms(shader)

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

        # --- Dibuja el suelo solo para los polígonos principales ---
        for poly_name, poly_vertices in map_data.polygons.items():
            if not poly_vertices or len(poly_vertices) < 3:
                continue

            floor_texture_name = map_data.polygon_floor_textures.get(poly_name)
            use_texture = floor_texture_name is not None

            glUniform1i(use_texture_loc, GL_TRUE if use_texture else GL_FALSE)

            if use_texture:
                texture_id = self.renderer.texture_manager.get_gl_texture_id(
                    floor_texture_name
                )
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glUniform1i(texture_sampler_loc, 0)
            else:
                floor_color_rgb = self.theme.get("floor", colors.DARK_GRAY)
                floor_color_gl = [c / 255.0 for c in floor_color_rgb]
                glUniform3f(color_loc, *floor_color_gl)

            floor_h = 0.0
            if hasattr(map_data, "sector_floor_h"):
                floor_h = map_data.sector_floor_h.get(poly_name, 0.0)

            # Preparación de Vértices (Posición + UVs)
            vertex_data = []
            for v in reversed(poly_vertices):
                vertex_data.extend(
                    [
                        v.x,
                        floor_h,
                        v.y,
                        v.x / tex_scale,
                        v.y / tex_scale,
                    ]
                )
            vertices = np.array(vertex_data, dtype=np.float32).reshape(-1, 5)

            # Usar FloorModel para encapsular el VBO y el dibujado
            model = FloorModel(vertices)
            pos_loc = glGetAttribLocation(shader, "position")
            uv_loc = glGetAttribLocation(shader, "texCoordIn")
            model.draw(shader, pos_loc, uv_loc)
            del model  # Libera el VBO

        glUseProgram(0)

    def _draw_ceilings(self, map_data: MapData, visible_segments: list[Segment]):
        """
        Dibuja el techo de todos los polígonos principales (sectores) usando un shader dedicado para techos.
        El techo se dibuja a la altura ceil_h de cada sector.
        """
        shader = getattr(self.renderer, "ceiling_shader_program", None)
        if not shader or not map_data.polygons:
            return

        glUseProgram(shader)

        # Enviar uniforms de iluminación dinámica (luz puntual y global)
        self.renderer.point_light.set_uniforms(shader)
        self.renderer.global_light.set_uniforms(shader)

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

        for poly_name, poly_vertices in map_data.polygons.items():
            if not poly_vertices or len(poly_vertices) < 3:
                continue

            ceil_texture_name = None
            if hasattr(map_data, "polygon_ceil_textures"):
                ceil_texture_name = map_data.polygon_ceil_textures.get(poly_name)
            use_texture = ceil_texture_name is not None

            glUniform1i(use_texture_loc, GL_TRUE if use_texture else GL_FALSE)

            if use_texture:
                texture_id = self.renderer.texture_manager.get_gl_texture_id(
                    ceil_texture_name
                )
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glUniform1i(texture_sampler_loc, 0)
            else:
                ceil_color_rgb = self.theme.get("ceiling", colors.LIGHT_GRAY)
                ceil_color_gl = [c / 255.0 for c in ceil_color_rgb]
                glUniform3f(color_loc, *ceil_color_gl)

            ceil_h = 0.0
            if hasattr(map_data, "sector_ceil_h"):
                ceil_h = map_data.sector_ceil_h.get(poly_name, 0.0)

            vertex_data = []
            for v in poly_vertices:
                vertex_data.extend(
                    [
                        v.x,
                        ceil_h,
                        v.y,
                        v.x / tex_scale,
                        v.y / tex_scale,
                    ]
                )
            vertices = np.array(vertex_data, dtype=np.float32).reshape(-1, 5)

            # Usar CeilingModel para encapsular el VBO y el dibujado
            model = CeilingModel(vertices)
            pos_loc = glGetAttribLocation(shader, "position")
            uv_loc = glGetAttribLocation(shader, "texCoordIn")
            model.draw(shader, pos_loc, uv_loc)
            del model

        glUseProgram(0)

    def _draw_3d_wall(self, seg: Segment, observer):
        """
        Dibuja un segmento de pared en 3D solo si la cara visible está orientada hacia el observador.
        El parámetro observer puede ser Player o MainCamera, siempre que tenga .pos.
        Soporta paredes sólidas y portales (divididas en secciones).
        """
        # --- Lógica de visibilidad de la cara ---
        wall_dx = seg.b.x - seg.a.x
        wall_dy = seg.b.y - seg.a.y
        normal_x = -wall_dy
        normal_y = wall_dx
        mid_x = (seg.a.x + seg.b.x) / 2
        mid_y = (seg.a.y + seg.b.y) / 2
        to_observer_x = observer.pos.x - mid_x
        to_observer_y = observer.pos.y - mid_y
        dot = normal_x * to_observer_x + normal_y * to_observer_y

        visible = True
        if seg.interior_facing is False:
            visible = dot > 0
        elif seg.interior_facing is True:
            visible = dot < 0

        if not visible:
            return

        shader = self.renderer.shader_program
        if not shader:
            return
        glUseProgram(shader)

        # Enviar uniforms de iluminación dinámica (luz puntual y global)
        self.renderer.point_light.set_uniforms(shader)
        self.renderer.global_light.set_uniforms(shader)

        tex_scale = (
            settings.TEXTURE_SCALE if hasattr(settings, "TEXTURE_SCALE") else 1.0
        )
        u_start = seg.u_offset / tex_scale
        u_end = (seg.u_offset + seg.length()) / tex_scale

        p1, p2 = seg.a, seg.b

        # --- Renderizado de portales: solo upper y lower, nunca pared sólida ---
        if getattr(seg, "wall_type", "solid") == "portal" and seg.portal_sections:
            for section in seg.portal_sections:
                # Solo dibujar upper y lower, omitir middle (hueco)
                if section["section"] not in ("top", "bottom"):
                    continue

                y1a = section["h1_a"]
                y1b = section["h1_b"]
                y2a = section["h2_a"]
                y2b = section["h2_b"]

                v_start_a = y1a / tex_scale
                v_start_b = y1b / tex_scale
                v_end_a = y2a / tex_scale
                v_end_b = y2b / tex_scale

                vertices = np.array(
                    [
                        [p1.x, y1a, p1.y, u_start, v_start_a],  # Abajo-Izquierda
                        [p2.x, y1b, p2.y, u_end, v_start_b],  # Abajo-Derecha
                        [p2.x, y2b, p2.y, u_end, v_end_b],  # Arriba-Derecha
                        [p1.x, y2a, p1.y, u_start, v_end_a],  # Arriba-Izquierda
                    ],
                    dtype=np.float32,
                )
                model = WallModel(vertices, wall_type="solid")
                pos_loc = glGetAttribLocation(shader, "position")
                uv_loc = glGetAttribLocation(shader, "texCoordIn")

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

                model.draw(shader, pos_loc, uv_loc)
                del model  # Libera el VBO
        else:
            # Pared sólida (comportamiento actual)
            y1a = getattr(seg, "portal_h1_a", 0.0)
            y1b = getattr(seg, "portal_h1_b", 0.0)
            y2a = getattr(
                seg,
                "portal_h2_a",
                seg.height if seg.height is not None else settings.WALL_HEIGHT,
            )
            y2b = getattr(
                seg,
                "portal_h2_b",
                seg.height if seg.height is not None else settings.WALL_HEIGHT,
            )

            v_start_a = y1a / tex_scale
            v_start_b = y1b / tex_scale
            v_end_a = y2a / tex_scale
            v_end_b = y2b / tex_scale

            vertices = np.array(
                [
                    [p1.x, y1a, p1.y, u_start, v_start_a],  # Abajo-Izquierda
                    [p2.x, y1b, p2.y, u_end, v_start_b],  # Abajo-Derecha
                    [p2.x, y2b, p2.y, u_end, v_end_b],  # Arriba-Derecha
                    [p1.x, y2a, p1.y, u_start, v_end_a],  # Arriba-Izquierda
                ],
                dtype=np.float32,
            )

            model = WallModel(vertices)
            pos_loc = glGetAttribLocation(shader, "position")
            uv_loc = glGetAttribLocation(shader, "texCoordIn")

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

            model.draw(shader, pos_loc, uv_loc)
            del model  # Libera el VBO

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

        # Dibujar el círculo de colisión real del jugador
        player_radius = getattr(settings, "PLAYER_COLLISION_RADIUS", 16.0)
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            angle = (i / 32) * 2 * math.pi
            glVertex2f(
                px + math.cos(angle) * player_radius,
                py + math.sin(angle) * player_radius,
            )
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
