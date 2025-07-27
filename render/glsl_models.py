"""
glsl_models.py

Modelos y métodos para el renderizado eficiente de paredes, suelos y techos usando OpenGL.
Cada clase encapsula la lógica de creación, actualización y destrucción de buffers (VBOs)
y el dibujo de su tipo de geometría, siguiendo principios SOLID, DRY y POO.
"""

from OpenGL.GL import *
import numpy as np
import ctypes


class GLSLModel:
    """
    Clase base para modelos OpenGL que gestionan VBOs y atributos.
    Proporciona métodos para crear, actualizar y destruir buffers.
    """

    def __init__(self):
        self.vbo = None
        self.vertex_count = 0

    def create_vbo(self, vertex_data: np.ndarray):
        """
        Crea un VBO con los datos de vértices proporcionados.
        """
        self.destroy_vbo()
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)
        self.vertex_count = len(vertex_data)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def destroy_vbo(self):
        """
        Libera el VBO si existe.
        """
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
            self.vbo = None

    def bind(self):
        """
        Enlaza el VBO para su uso.
        """
        if self.vbo:
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

    def unbind(self):
        """
        Desenlaza el VBO.
        """
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def __del__(self):
        self.destroy_vbo()


class WallModel(GLSLModel):
    """
    Modelo para renderizar una pared, soportando tanto paredes sólidas como portales al estilo Doom clásico.
    Permite invertir la normal del quad para que los escalones sean visibles desde ambos lados.
    """

    def __init__(
        self,
        vertices: np.ndarray,
        wall_type: str = "solid",
        portal_sections: list = None,
        sector_heights: dict = None,
    ):
        """
        Inicializa el modelo de pared.
        - vertices: np.ndarray de shape (4, 5) para sólido, o extremos para portal.
        - wall_type: 'solid' o 'portal'.
        - portal_sections: lista de dicts con info de cada sección (solo para portal).
        - sector_heights: dict con alturas de ambos sectores (solo para portal).
        """
        super().__init__()
        self.wall_type = wall_type
        self.portal_sections = portal_sections or []
        self.sector_heights = sector_heights or {}
        self.vertices = vertices  # Guardamos los extremos para portal
        if wall_type == "solid":
            # Para sólido, creamos el VBO directamente
            self.create_vbo(vertices)

    def draw(self, shader_program, pos_loc, uv_loc):
        """
        Dibuja la pared usando el shader y los atributos dados.
        Si invert_normal=True, invierte el sentido de los vértices para invertir la normal.
        """
        if self.wall_type == "solid":
            quad_vertices = self.vertices
            self.create_vbo(quad_vertices)
            self.bind()
            glEnableVertexAttribArray(pos_loc)
            glVertexAttribPointer(pos_loc, 3, GL_FLOAT, False, 20, ctypes.c_void_p(0))
            glEnableVertexAttribArray(uv_loc)
            glVertexAttribPointer(uv_loc, 2, GL_FLOAT, False, 20, ctypes.c_void_p(12))
            glDrawArrays(GL_QUADS, 0, 4)
            glDisableVertexAttribArray(pos_loc)
            glDisableVertexAttribArray(uv_loc)
            self.unbind()
            self.destroy_vbo()
        elif (
            self.wall_type == "portal" and self.portal_sections and self.sector_heights
        ):
            # --- Pared portal: dibujar solo Lower y Upper, omitir Middle ---
            # Se espera que self.vertices contenga los extremos [p1, p2] como Vec3 (x, y, z)
            p1 = self.vertices[0]
            p2 = self.vertices[1]
            # Alturas de ambos sectores
            own_floor = self.sector_heights.get("own_floor", 0.0)
            own_ceil = self.sector_heights.get("own_ceil", 0.0)
            adj_floor = self.sector_heights.get("adj_floor", 0.0)
            adj_ceil = self.sector_heights.get("adj_ceil", 0.0)
            tex_scale = self.sector_heights.get("tex_scale", 1.0)
            u_start = self.sector_heights.get("u_start", 0.0)
            u_end = self.sector_heights.get("u_end", 1.0)

            for section in self.portal_sections:
                # Solo dibujar las secciones lower y upper (middle es hueco)
                if section["section"] == "bottom":
                    # Lower: desde el suelo del sector adyacente hasta el suelo propio
                    y1a = adj_floor
                    y1b = adj_floor
                    y2a = own_floor
                    y2b = own_floor
                elif section["section"] == "top":
                    # Upper: desde el techo propio hasta el techo del sector adyacente
                    y1a = own_ceil
                    y1b = own_ceil
                    y2a = adj_ceil
                    y2b = adj_ceil
                else:
                    # No dibujar la sección 'middle'
                    continue

                # Calcular UVs para cada vértice
                v_start_a = y1a / tex_scale
                v_start_b = y1b / tex_scale
                v_end_a = y2a / tex_scale
                v_end_b = y2b / tex_scale

                quad_vertices = np.array(
                    [
                        [p1[0], y1a, p1[2], u_start, v_start_a],  # Abajo-Izquierda
                        [p2[0], y1b, p2[2], u_end, v_start_b],  # Abajo-Derecha
                        [p2[0], y2b, p2[2], u_end, v_end_b],  # Arriba-Derecha
                        [p1[0], y2a, p1[2], u_start, v_end_a],  # Arriba-Izquierda
                    ],
                    dtype=np.float32,
                )
                # Crear VBO temporal para la sección y dibujar
                self.create_vbo(quad_vertices)
                self.bind()
                glEnableVertexAttribArray(pos_loc)
                glVertexAttribPointer(
                    pos_loc, 3, GL_FLOAT, False, 20, ctypes.c_void_p(0)
                )
                glEnableVertexAttribArray(uv_loc)
                glVertexAttribPointer(
                    uv_loc, 2, GL_FLOAT, False, 20, ctypes.c_void_p(12)
                )
                glDrawArrays(GL_QUADS, 0, 4)
                glDisableVertexAttribArray(pos_loc)
                glDisableVertexAttribArray(uv_loc)
                self.unbind()
                self.destroy_vbo()
        else:
            # Si no hay datos suficientes, no se dibuja nada
            pass


class FloorModel(GLSLModel):
    """
    Modelo para renderizar un polígono de suelo.
    """

    def __init__(self, vertices: np.ndarray):
        """
        vertices: np.ndarray de shape (N, 5) -> [x, y, z, u, v] por vértice
        """
        super().__init__()
        self.create_vbo(vertices)

    def draw(self, shader_program, pos_loc, uv_loc):
        """
        Dibuja el suelo usando el shader y los atributos dados.
        """
        self.bind()
        glEnableVertexAttribArray(pos_loc)
        glVertexAttribPointer(pos_loc, 3, GL_FLOAT, False, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(uv_loc)
        glVertexAttribPointer(uv_loc, 2, GL_FLOAT, False, 20, ctypes.c_void_p(12))
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.vertex_count)
        glDisableVertexAttribArray(pos_loc)
        glDisableVertexAttribArray(uv_loc)
        self.unbind()


class CeilingModel(GLSLModel):
    """
    Modelo para renderizar un polígono de techo.
    """

    def __init__(self, vertices: np.ndarray):
        """
        vertices: np.ndarray de shape (N, 5) -> [x, y, z, u, v] por vértice
        """
        super().__init__()
        self.create_vbo(vertices)

    def draw(self, shader_program, pos_loc, uv_loc):
        """
        Dibuja el techo usando el shader y los atributos dados.
        """
        self.bind()
        glEnableVertexAttribArray(pos_loc)
        glVertexAttribPointer(pos_loc, 3, GL_FLOAT, False, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(uv_loc)
        glVertexAttribPointer(uv_loc, 2, GL_FLOAT, False, 20, ctypes.c_void_p(12))
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.vertex_count)
        glDisableVertexAttribArray(pos_loc)
        glDisableVertexAttribArray(uv_loc)
        self.unbind()
