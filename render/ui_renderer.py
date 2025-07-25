"""
UI Renderer for GLFW OpenGL Application using modern OpenGL.
"""

from OpenGL.GL import *
import numpy as np
import ctypes


class UIRenderer:
    def __init__(self, renderer):
        """
        Inicializa el renderizador de UI, creando los recursos de OpenGL necesarios.
        """
        self.renderer = renderer
        self.shader = renderer.ui_shader_program

        # Geometría de un quad (cuadrado) de 1x1. Lo reutilizaremos para todos los botones.
        quad_vertices = np.array(
            [
                # positions
                0.0,
                1.0,  # Top-left
                0.0,
                0.0,  # Bottom-left
                1.0,
                0.0,  # Bottom-right
                1.0,
                1.0,  # Top-right
            ],
            dtype=np.float32,
        )

        indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

        # Crear Vertex Array Object (VAO), Vertex Buffer Object (VBO), y Element Buffer Object (EBO)
        self.quad_vao = glGenVertexArrays(1)
        self.quad_vbo = glGenBuffers(1)
        self.quad_ebo = glGenBuffers(1)

        glBindVertexArray(self.quad_vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.quad_vbo)
        glBufferData(
            GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW
        )

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.quad_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # Definir el layout de los atributos de vértice
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(ctypes.c_float), ctypes.c_void_p(0)
        )
        glEnableVertexAttribArray(0)

        # Desvincular para evitar modificaciones accidentales
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw_main_menu(self, options, selected_index):
        """
        Dibuja el menú principal usando shaders, matrices y un único VAO.
        """
        width, height = self.renderer.width, self.renderer.height

        # Limpiar la pantalla
        glDisable(GL_DEPTH_TEST)  # La UI no necesita test de profundidad
        glDisable(GL_CULL_FACE)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Activar el shader de la UI
        glUseProgram(self.shader)

        # Crear una matriz de proyección ortográfica
        # Esto mapea las coordenadas de píxeles de la pantalla a las coordenadas de OpenGL (-1 a 1)
        projection = np.array(
            [
                [2.0 / width, 0, 0, -1],
                [0, -2.0 / height, 0, 1],
                [0, 0, -1, 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        ).T

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection
        )

        # Parámetros de los botones
        btn_w, btn_h = 300, 60
        spacing = 40
        start_y = height / 2 - (len(options) * (btn_h + spacing) - spacing) / 2

        # Vincular el VAO del quad que vamos a reutilizar
        glBindVertexArray(self.quad_vao)

        for i, opt in enumerate(options):
            x = (width - btn_w) / 2
            y = start_y + i * (btn_h + spacing)

            # Crear la matriz de modelo para este botón específico
            # Escalar nuestro quad de 1x1 al tamaño del botón
            scale_matrix = np.diag([btn_w, btn_h, 1, 1]).astype(np.float32)
            # Mover el quad escalado a su posición en la pantalla
            trans_matrix = np.identity(4, dtype=np.float32)
            trans_matrix[3, 0] = x
            trans_matrix[3, 1] = y

            model = scale_matrix @ trans_matrix

            glUniformMatrix4fv(
                glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model
            )

            # Invertir los colores de selección
            if i == selected_index:
                color = (0.5, 0.5, 0.5)  # Gris para el seleccionado
            else:
                color = (1.0, 1.0, 1.0)  # Blanco para los no seleccionados

            glUniform3f(glGetUniformLocation(self.shader, "objectColor"), *color)

            # Dibujar el quad (6 vértices del EBO)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # Desvincular todo
        glBindVertexArray(0)
        glUseProgram(0)

    def cleanup(self):
        """
        Libera los recursos de OpenGL (VAO, VBO, EBO) cuando ya no se necesiten.
        """
        glDeleteVertexArrays(1, [self.quad_vao])
        glDeleteBuffers(1, [self.quad_vbo, self.quad_ebo])
