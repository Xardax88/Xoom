"""
Camera2D: Gestión de la cámara 2D para OpenGL con GLFW.
    Esta clase permite manejar la vista 2D, aplicar transformaciones y centrar la cámara en un objetivo.

MainCamera: Cámara principal para la vista 3D, desacoplada del jugador.
    Permite posicionar la cámara en el mundo y seguir al jugador.
"""

from __future__ import annotations
from dataclasses import dataclass

# Importamos las funciones de OpenGL que necesitaremos para la transformación
from OpenGL.GL import (
    glLoadIdentity,
    glMatrixMode,
    glScalef,
    glTranslatef,
    glOrtho,
    GL_MODELVIEW,
    GL_PROJECTION,
)
from core._types import Vec2  # Importar Vec2 para la propiedad pos


@dataclass
class Camera2D:
    """
    Gestiona la vista 2D y aplica las transformaciones
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

        glTranslatef(self.width / 2.0, self.height / 2.0, 0)

        glScalef(self.scale, self.scale, 1.0)

        glTranslatef(-self.x, -self.y, 0)

    def update_viewport(self, width: int, height: int) -> None:
        """Actualiza las dimensiones de la cámara, útil al redimensionar la ventana."""
        self.width = width
        self.height = height


@dataclass
class MainCamera:
    """
    Cámara principal para la vista 3D.
    Permite posicionar la cámara en el mundo y seguir al jugador.
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    angle_deg: float = 0.0
    fov_deg: float = 90.0  # FOV horizontal de la cámara, sincronizado con el jugador

    @property
    def pos(self) -> Vec2:
        """
        Devuelve la posición de la cámara como un objeto Vec2 (x, z).
        Esto permite compatibilidad polimórfica con Player.
        """
        return Vec2(self.x, self.z)

    def set_position(self, x: float, y: float, z: float) -> None:
        """Posiciona la cámara en el mundo."""
        self.x = x
        self.y = y
        self.z = z

    def set_angle(self, angle_deg: float) -> None:
        """Establece el ángulo de la cámara."""
        self.angle_deg = angle_deg

    def set_fov(self, fov_deg: float) -> None:
        """Establece el FOV horizontal de la cámara."""
        self.fov_deg = fov_deg

    def follow_player(self, player) -> None:
        """
        Centra la cámara en la posición, ángulo y FOV del jugador.
        Esto asegura que la proyección y la lógica de visibilidad sean consistentes.
        """
        self.x = player.x
        self.y = getattr(player, "z", 0.0)  # Si el jugador tiene altura z
        self.z = player.y
        self.angle_deg = player.angle_deg
        # Sincronizar el FOV de la cámara con el del jugador
        self.fov_deg = getattr(player, "fov_deg", 90.0)

    # Métodos adicionales para interpolación, efectos, etc. pueden añadirse aquí.


@dataclass
class HUDCamera:
    """
    HUDCamera: Cámara 2D para renderizar el HUD (información en pantalla).
    Permite transformar la matriz de OpenGL para dibujar elementos del HUD en coordenadas de pantalla.
    El origen (0,0) está en la esquina superior izquierda.
    """

    width: int
    height: int

    def apply_transform(self) -> None:
        """
        Aplica la transformación ortográfica para el HUD.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def update_viewport(self, width: int, height: int) -> None:
        """
        Actualiza las dimensiones del HUD, útil al redimensionar la ventana.
        """
        self.width = width
        self.height = height
