"""
UILabel: Clase para representar y renderizar una etiqueta de HUD (texto en pantalla) usando OpenGL y shaders.
Centraliza la lógica de generación de textura, gestión de fuente y renderizado, cumpliendo SOLID, DRY y POO.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict
from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import settings


@dataclass
class UILabel:
    text: str
    x: int
    y: int
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    bg_color: Tuple[int, int, int, int] = (0, 0, 0, 180)
    font_size: int = 36  # Tamaño de fuente para el texto de la etiqueta
    border_color: Tuple[int, int, int, int] = (0, 0, 0, 255)  # Color del borde
    border_width: int = 2  # Grosor del borde en píxeles

    # Cache de texturas y fuentes por tamaño para evitar recreación innecesaria
    _font_cache: Dict[int, ImageFont.FreeTypeFont] = field(
        default_factory=dict, init=False, repr=False
    )
    _texture_cache: Dict[
        Tuple[str, Tuple[int, int, int, int], int, Tuple[int, int, int, int], int],
        Tuple[int, int, int],
    ] = field(default_factory=dict, init=False, repr=False)

    def _get_font(self) -> ImageFont.FreeTypeFont:
        """
        Obtiene (o crea) la fuente TTF para el tamaño especificado.
        """
        if self.font_size not in self._font_cache:
            font_path = str(settings.FONTS_DIR / "hack_nerd.ttf")
            if not os.path.exists(font_path):
                raise FileNotFoundError(f"Fuente TTF no encontrada: {font_path}")
            self._font_cache[self.font_size] = ImageFont.truetype(
                font_path, self.font_size
            )
        return self._font_cache[self.font_size]

    def get_text_texture(self) -> Tuple[int, int, int]:
        """
        Devuelve (tex_id, width, height) para el texto de la etiqueta, usando caché.
        Utiliza stroke_width y stroke_fill de Pillow para dibujar el borde de forma eficiente.
        """
        key = (
            self.text,
            self.color,
            self.font_size,
            self.border_color,
            self.border_width,
        )
        if key in self._texture_cache:
            return self._texture_cache[key]

        font = self._get_font()
        # Medir el tamaño del texto usando textbbox (considerando el borde)
        dummy_img = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        text_bbox = draw.textbbox(
            (0, 0),
            self.text,
            font=font,
            stroke_width=self.border_width,
        )
        width = text_bbox[2] - text_bbox[0]
        height = text_bbox[3] - text_bbox[1]

        ascent, descent = font.getmetrics()
        margin_top = int(height * 0.1)
        margin_bottom = int(height * 0.1 + descent)

        img_w = width
        img_h = height + margin_top + margin_bottom

        # Crear imagen con fondo transparente y márgenes
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Dibujar el texto principal con borde usando stroke_width y stroke_fill
        draw.text(
            (0, margin_top),
            self.text,
            font=font,
            fill=self.color,
            stroke_width=self.border_width,
            stroke_fill=self.border_color,
        )

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
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # Generar mipmaps
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)

        self._texture_cache[key] = (tex_id, img_w, img_h)
        return tex_id, img_w, img_h

    def draw(self, shader_program: int, width: int, height: int, vao: int):
        """
        Renderiza la etiqueta usando el shader y el VAO proporcionados.
        """
        tex_id, tex_w, tex_h = self.get_text_texture()
        x = self.x
        y = self.y

        # Deshabilitar profundidad y culling para UI
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        glUseProgram(shader_program)

        # Matriz de proyección ortográfica para pantalla completa
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
            glGetUniformLocation(shader_program, "projection"),
            1,
            GL_FALSE,
            projection,
        )

        # Pasar uniforms de posición y tamaño de la etiqueta
        glUniform2f(glGetUniformLocation(shader_program, "labelPos"), x, y)
        glUniform2f(glGetUniformLocation(shader_program, "labelSize"), tex_w, tex_h)

        # Dibujar fondo semitransparente para mejorar legibilidad
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(
            self.bg_color[0] / 255.0,
            self.bg_color[1] / 255.0,
            self.bg_color[2] / 255.0,
            self.bg_color[3] / 255.0,
        )
        glBegin(GL_QUADS)
        glVertex2f(x - 6, y - 4)
        glVertex2f(x - 6, y + tex_h + 4)
        glVertex2f(x + tex_w + 6, y + tex_h + 4)
        glVertex2f(x + tex_w + 6, y - 4)
        glEnd()
        glDisable(GL_BLEND)

        # Configurar textura y uniforms para el shader
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glUniform1i(glGetUniformLocation(shader_program, "textTexture"), 0)
        glUniform1i(glGetUniformLocation(shader_program, "useTexture"), 1)

        # Dibujar el quad usando el VAO/VBO configurado
        glBindVertexArray(vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glColor3f(1, 1, 1)  # Restaurar color

    def cleanup(self):
        """
        Libera las texturas generadas por la etiqueta.
        """
        for tex_id, _, _ in self._texture_cache.values():
            glDeleteTextures([tex_id])
        self._texture_cache.clear()

    @classmethod
    def cleanup_fonts(cls):
        """
        Limpia la caché de fuentes.
        """
        cls._font_cache.clear()
