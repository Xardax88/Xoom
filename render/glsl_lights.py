"""
glsl_lights.py

Define la clase PointLight para representar y gestionar una luz puntual en el motor 3D.
Incluye métodos para modificar sus parámetros y para enviar los uniformes a los shaders GLSL.
Esto separa la lógica de iluminación del renderer principal, siguiendo SRP y SOLID.
"""

import numpy as np
from OpenGL.GL import (
    glGetUniformLocation,
    glUniform3fv,
    glUniform1f,
    glGetIntegerv,
    GL_CURRENT_PROGRAM,
)
import logging

logger = logging.getLogger(__name__)


class PointLight:
    """
    Representa una luz puntual simple para el motor.
    Permite modificar posición, color, intensidad y rango de la luz.
    Además, puede enviar sus parámetros como uniformes a un shader GLSL.
    Esta clase puede ser extendida para soportar múltiples luces o tipos de luz en el futuro.
    """

    def __init__(
        self,
        position=(0.0, 128.0, 0.0),
        color=(1.0, 1.0, 1.0),
        intensity=1.0,
        range=500.0,
    ):
        # Posición de la luz en el espacio 3D (x, y, z)
        self.position = np.array(position, dtype=np.float32)
        # Color de la luz (RGB, valores entre 0.0 y 1.0)
        self.color = np.array(color, dtype=np.float32)
        # Intensidad de la luz (float)
        self.intensity = float(intensity)
        # Rango máximo de iluminación (float, en unidades del mundo)
        self.range = float(range)

    def set(self, position=None, color=None, intensity=None, range=None):
        """
        Permite modificar los parámetros de la luz puntual.
        - position: tupla o array con la nueva posición (x, y, z)
        - color: tupla o array con el nuevo color (r, g, b)
        - intensity: nuevo valor de intensidad (float)
        - range: nuevo rango de iluminación (float)
        """
        if position is not None:
            self.position = np.array(position, dtype=np.float32)
        if color is not None:
            self.color = np.array(color, dtype=np.float32)
        if intensity is not None:
            self.intensity = float(intensity)
        if range is not None:
            self.range = float(range)

    def set_uniforms(self, shader_program):
        """
        Envía los parámetros de la luz puntual como uniformes al shader activo.
        IMPORTANTE: El shader debe estar activo (glUseProgram(shader_program)) antes de llamar a este método.
        Si el shader no está activo, no se realiza ninguna operación y se registra una advertencia.
        """
        if not shader_program:
            return
        # Comprobación defensiva: ¿el shader está activo?
        current_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        if current_program != shader_program:
            logger.warning(
                "Intento de setear uniformes de luz en un shader no activo. "
                "Llama a glUseProgram(shader_program) antes de set_uniforms."
            )
            return
        pos_loc = glGetUniformLocation(shader_program, "lightPosition")
        color_loc = glGetUniformLocation(shader_program, "lightColor")
        intensity_loc = glGetUniformLocation(shader_program, "lightIntensity")
        range_loc = glGetUniformLocation(shader_program, "lightRange")
        if pos_loc != -1:
            glUniform3fv(pos_loc, 1, self.position)
        if color_loc != -1:
            glUniform3fv(color_loc, 1, self.color)
        if intensity_loc != -1:
            glUniform1f(intensity_loc, self.intensity)
        if range_loc != -1:
            glUniform1f(range_loc, self.range)


class GlobalLight:
    """
    Representa una luz global ambiental para el motor.
    Permite modificar color e intensidad, y enviar sus parámetros como uniformes.
    """

    def __init__(self, color=(1.0, 1.0, 1.0), intensity=0.3):
        self.color = np.array(color, dtype=np.float32)
        self.intensity = float(intensity)

    def set(self, color=None, intensity=None):
        """
        Modifica los parámetros de la luz global.
        - color: tupla o array con el nuevo color (r, g, b)
        - intensity: nuevo valor de intensidad (float)
        """
        if color is not None:
            self.color = np.array(color, dtype=np.float32)
        if intensity is not None:
            self.intensity = float(intensity)

    def set_uniforms(self, shader_program):
        """
        Envía los parámetros de la luz global como uniformes al shader activo.
        """
        if not shader_program:
            return
        current_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        if current_program != shader_program:
            logger.warning(
                "Intento de setear uniformes de luz global en un shader no activo."
            )
            return
        color_loc = glGetUniformLocation(shader_program, "globalLightColor")
        intensity_loc = glGetUniformLocation(shader_program, "globalLightIntensity")
        if color_loc != -1:
            glUniform3fv(color_loc, 1, self.color)
        if intensity_loc != -1:
            glUniform1f(intensity_loc, self.intensity)
