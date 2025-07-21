"""
Cámara 2D para gestionar la vista en el mundo del juego.
"""

from __future__ import annotations
from dataclasses import dataclass

# Importamos las funciones de OpenGL que necesitaremos para la transformación
from OpenGL.GL import glLoadIdentity, glMatrixMode, glScalef, glTranslatef, GL_MODELVIEW


@dataclass
class Camera2D:
    """
    Gestiona la vista 2D (posición, zoom) y aplica las transformaciones
    a la matriz de OpenGL.
    """

    width: int
    height: int
    scale: float = 1.0
    x: float = 0.0
    y: float = 0.0

    def set_target(self, target_x: float, target_y: float) -> None:
        """Actualiza la posición de la cámara para centrarse en un punto."""
        self.x = target_x
        self.y = target_y

    def apply_transform(self) -> None:
        """
        Aplica las transformaciones de la cámara a la matriz MODELVIEW de OpenGL.
        Esto debe llamarse una vez por frame, antes de dibujar cualquier objeto del mundo.
        """
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # 1. Mover el origen (0,0) al centro de la pantalla.
        glTranslatef(self.width / 2.0, self.height / 2.0, 0)

        # 2. Aplicar el zoom (escala).
        glScalef(self.scale, self.scale, 1.0)

        # 3. Mover el mundo para que el objetivo de la cámara quede en el centro.
        #    Se usa la posición negativa del objetivo.
        glTranslatef(-self.x, -self.y, 0)

    def update_viewport(self, width: int, height: int) -> None:
        """Actualiza las dimensiones de la cámara, útil al redimensionar la ventana."""
        self.width = width
        self.height = height
