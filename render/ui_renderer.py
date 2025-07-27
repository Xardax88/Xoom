"""
UIRenderer: Módulo para renderizar la interfaz de usuario (UI) en OpenGL.
"""

from OpenGL.GL import *
import numpy as np
import ctypes
from PIL import Image, ImageDraw, ImageFont
import settings
import os
from .ui_label import UILabel
from .minimap_renderer import MinimapRenderer


class TextTextureManager:
    """
    Encapsula la lógica para crear y gestionar texturas OpenGL a partir de texto TTF usando Pillow.
    Cumple con SOLID y DRY, y es fácilmente reutilizable.
    """

    def __init__(self, font_path: str, font_size: int):
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Fuente TTF no encontrada: {font_path}")
        self.font = ImageFont.truetype(font_path, font_size)
        self._texture_cache = {}

    def get_text_texture(self, text: str, color=(0, 0, 0, 255)) -> tuple:
        """
        Devuelve (tex_id, width, height) para el texto dado.
        Usa caché para evitar recrear texturas.
        Corrige la orientación vertical y añade margen para evitar cortes.
        Ajusta el margen inferior usando ascent y descent para evitar recorte por debajo.
        """
        key = (text, color)
        if key in self._texture_cache:
            return self._texture_cache[key]

        # Medir el tamaño del texto usando textbbox
        dummy_img = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        text_bbox = draw.textbbox((0, 0), text, font=self.font)
        width = text_bbox[2] - text_bbox[0]
        height = text_bbox[3] - text_bbox[1]

        # Obtener ascent y descent de la fuente para ajustar el margen inferior
        ascent, descent = self.font.getmetrics()
        # Añadir margen superior e inferior (10% del alto visual)
        margin_top = int(height * 0.1)
        margin_bottom = int(height * 0.1 + descent)

        img_w = width
        img_h = height + margin_top + margin_bottom

        # Crear imagen con fondo transparente y márgenes
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Dibujar el texto desplazado hacia abajo por el margen superior
        draw.text((0, margin_top), text, font=self.font, fill=color)

        # Corregir la orientación vertical del texto
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        img_data = img.tobytes("raw", "RGBA", 0, -1)
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            img_w,
            img_h,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data,
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        self._texture_cache[key] = (tex_id, img_w, img_h)
        return tex_id, img_w, img_h

    def cleanup(self):
        """
        Libera todas las texturas generadas.
        """
        for tex_id, _, _ in self._texture_cache.values():
            glDeleteTextures([tex_id])
        self._texture_cache.clear()


class UIRenderer:
    """
    Renderizador de la interfaz de usuario, incluyendo botones con texto TTF usando shaders y texturas.
    Integra el renderizado del minimapa usando MinimapRenderer, siguiendo SOLID y POO.
    """

    def __init__(self, renderer):
        self.renderer = renderer
        self.shader = getattr(self.renderer, "ui_button_shader_program", None)
        self.label_shader = getattr(self.renderer, "ui_label_shader_program", None)

        # --- VAO/VBO/EBO para quads genéricos de UI (botones del menú principal) ---
        # Este quad se usa para los botones del menú principal (draw_main_menu)
        quad_vertices = np.array(
            [
                0.0,
                0.0,  # Inferior izquierda
                1.0,
                0.0,  # Inferior derecha
                1.0,
                1.0,  # Superior derecha
                0.0,
                1.0,  # Superior izquierda
            ],
            dtype=np.float32,
        )
        indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

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
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(ctypes.c_float), ctypes.c_void_p(0)
        )
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # --- VAO/VBO/EBO para etiquetas HUD ---
        # Este quad se usa para las etiquetas HUD (draw_label)
        self.label_vao = glGenVertexArrays(1)
        self.label_vbo = glGenBuffers(1)
        self.label_ebo = glGenBuffers(1)

        glBindVertexArray(self.label_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.label_vbo)
        glBufferData(
            GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW
        )
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.label_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(ctypes.c_float), ctypes.c_void_p(0)
        )
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # Diccionario para gestionar TextTextureManager por tamaño de fuente
        self._font_managers = {}
        # Inicializar el gestor de texturas de texto por defecto (36)
        font_path = str(settings.FONTS_DIR / "hack_nerd.ttf")
        self.text_texture_manager = TextTextureManager(font_path, 36)
        self._font_managers[36] = self.text_texture_manager

        # --- Integración del minimapa ---
        # Instancia responsable de renderizar el minimapa usando shaders dedicados.
        # Se recomienda actualizar la textura del mapa y la posición del jugador desde el exterior usando los métodos públicos.
        self.minimap_renderer = MinimapRenderer()
        # Ejemplo de cómo asignar la textura del mapa y la posición del jugador:
        # self.minimap_renderer.set_map_texture(texture_id)
        # self.minimap_renderer.set_player_position(x_normalized, y_normalized)

    def draw_main_menu(self, options, selected_index):
        """
        Dibuja el menú principal con botones y texto TTF centrado usando shaders y texturas.
        """
        width, height = self.renderer.width, self.renderer.height

        # Limpiar la pantalla y configurar OpenGL para UI
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(self.shader)

        # Matriz de proyección ortográfica
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

        btn_w, btn_h = 300, 60
        spacing = 40
        start_y = height / 2 - (len(options) * (btn_h + spacing) - spacing) / 2

        glBindVertexArray(self.quad_vao)

        for i, opt in enumerate(options):
            x = (width - btn_w) / 2
            y = start_y + i * (btn_h + spacing)

            # Matriz de modelo para escalar y posicionar el botón
            scale_matrix = np.diag([btn_w, btn_h, 1, 1]).astype(np.float32)
            trans_matrix = np.identity(4, dtype=np.float32)
            trans_matrix[3, 0] = x
            trans_matrix[3, 1] = y
            model = scale_matrix @ trans_matrix
            glUniformMatrix4fv(
                glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model
            )

            # Color de fondo del botón
            # CORREGIDO: El botón seleccionado ahora es blanco, los demás son grises
            if i == selected_index:
                color = (1.0, 1.0, 1.0)  # Blanco para el seleccionado
            else:
                color = (0.5, 0.5, 0.5)  # Gris para los no seleccionados
            glUniform3f(glGetUniformLocation(self.shader, "objectColor"), *color)

            # --- Renderizado del texto como textura ---
            if isinstance(opt, str):
                text = opt
            elif hasattr(opt, "label"):
                text = opt.label
            else:
                text = str(opt)

            # Generar textura del texto
            tex_id, tex_w, tex_h = self.text_texture_manager.get_text_texture(
                text, color=(0, 0, 0, 255)
            )

            # Calcular posición y tamaño del texto relativo al botón
            text_scale_x = tex_w / btn_w
            text_scale_y = tex_h / btn_h
            # Offset para centrar el texto en el quad del botón (en espacio local [0,1])
            offset_x = (1.0 - text_scale_x) / 2.0
            offset_y = (1.0 - text_scale_y) / 2.0

            # Pasar uniforms para el shader
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glUniform1i(glGetUniformLocation(self.shader, "textTexture"), 0)
            glUniform1i(glGetUniformLocation(self.shader, "useTexture"), 1)
            glUniform2f(
                glGetUniformLocation(self.shader, "textOffset"), offset_x, offset_y
            )
            glUniform2f(
                glGetUniformLocation(self.shader, "textScale"),
                text_scale_x,
                text_scale_y,
            )

            # Dibujar el botón con textura de texto
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

            # Limpiar estado para el siguiente botón
            glBindTexture(GL_TEXTURE_2D, 0)
            glUniform1i(glGetUniformLocation(self.shader, "useTexture"), 0)

        glBindVertexArray(0)
        glUseProgram(0)

        # Renderiza el minimapa en la UI principal (puedes mover esto a otro método si lo deseas en todo momento)
        if self.minimap_renderer:
            self.minimap_renderer.render()

    def draw_label(self, label: UILabel, width: int, height: int):
        """
        Dibuja una etiqueta HUD usando el shader ui_label_shader_program.
        Ahora delega toda la lógica a UILabel.draw, cumpliendo SOLID y DRY.
        """
        if not self.label_shader:
            return
        label.draw(self.label_shader, width, height, self.label_vao)

    def cleanup(self):
        """
        Libera los recursos de OpenGL (VAO, VBO, EBO) y texturas de texto.
        """
        glDeleteVertexArrays(1, [self.label_vao])
        glDeleteBuffers(1, [self.label_vbo, self.label_ebo])
        glDeleteVertexArrays(1, [self.quad_vao])
        glDeleteBuffers(1, [self.quad_vbo, self.quad_ebo])
        # Limpiar todas las texturas de las etiquetas
        UILabel.cleanup_fonts()
