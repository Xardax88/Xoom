"""
Barra de menú superior para el editor de mapas.
Permite cargar y guardar archivos .xmap.
"""

import pygame
from OpenGL.GL import *


class MenuBar:
    """
    Barra de menú superior con botones de 'Cargar', 'Guardar' y 'Deshacer'.
    """

    def __init__(self, editor_window, width, height):
        self.editor_window = editor_window
        self.width = width
        self.height = height
        self.buttons = [
            {
                "label": "Cargar",
                "rect": pygame.Rect(10, 5, 80, 30),
                "action": self.load_map,
            },
            {
                "label": "Guardar",
                "rect": pygame.Rect(100, 5, 80, 30),
                "action": self.save_map,
            },
            {
                "label": "Deshacer",
                "rect": pygame.Rect(190, 5, 80, 30),
                "action": self.undo_last,
            },
        ]

    def draw(self):
        """
        Dibuja la barra de menú y los botones.
        """
        # Fondo del menú
        glColor3f(0.15, 0.15, 0.18)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        # Botones (solo el contorno, el texto requiere renderizado extra)
        for btn in self.buttons:
            x, y, w, h = btn["rect"]
            glColor3f(0.3, 0.3, 0.4)
            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + w, y)
            glVertex2f(x + w, y + h)
            glVertex2f(x, y + h)
            glEnd()
        # Nota: El texto de los botones puede renderizarse con pygame.font sobre una superficie y luego como textura.

    def handle_event(self, event):
        """
        Maneja los clics en los botones del menú.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    btn["action"]()

    def load_map(self):
        """
        Acción para cargar un mapa (puedes mejorar con un diálogo de archivos).
        """
        # Por simplicidad, pide el path por consola
        filepath = input("Ruta del archivo .xmap a cargar: ")
        self.editor_window.load_map(filepath)

    def save_map(self):
        """
        Acción para guardar el mapa (puedes mejorar con un diálogo de archivos).
        """
        filepath = input("Ruta destino para guardar .xmap: ")
        self.editor_window.save_map(filepath)

    def undo_last(self):
        """
        Acción para deshacer el último sector agregado.
        """
        self.editor_window.undo_last_sector()
