"""
Permite al usuario dibujar y editar sectores sobre la cuadrícula.
"""

import OpenGL.GL as gl
import pygame


class SectorDrawer:
    """
    Permite al usuario dibujar y editar sectores sobre el canvas.
    """

    def __init__(self, map_data, offset_y=40):
        self.map_data = map_data
        self.current_points = []
        self.offset_y = offset_y  # Para dejar espacio al menú

    def handle_event(self, event):
        """
        Maneja los eventos de mouse y teclado para dibujar sectores.
        - Click izquierdo: agrega un punto al sector actual.
        - Click derecho: cierra el sector actual si tiene al menos 3 puntos.
        - Enter: también cierra el sector.
        - Backspace: elimina el último punto del sector actual.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if event.button == 1 and y > self.offset_y:
                # Click izquierdo: agregar punto
                self.current_points.append((x, y))
            elif event.button == 3 and y > self.offset_y:
                # Click derecho: cerrar sector si hay al menos 3 puntos
                if len(self.current_points) > 2:
                    self.map_data.add_sector(self.current_points.copy())
                    self.current_points.clear()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # Enter: cerrar sector si hay al menos 3 puntos
            if len(self.current_points) > 2:
                self.map_data.add_sector(self.current_points.copy())
                self.current_points.clear()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            # Backspace: eliminar último punto
            if self.current_points:
                self.current_points.pop()

    def draw(self):
        """
        Dibuja los puntos y líneas del sector actual y los sectores existentes.
        """
        # Dibuja sectores existentes
        for sector in self.map_data.sectors:
            gl.glColor3f(0.2, 0.8, 0.2)
            gl.glBegin(gl.GL_LINE_LOOP)
            for x, y in sector:
                gl.glVertex2f(x, y)
            gl.glEnd()
        # Dibuja el sector en edición
        if self.current_points:
            gl.glColor3f(1.0, 0.5, 0.0)
            gl.glBegin(gl.GL_LINE_STRIP)
            for x, y in self.current_points:
                gl.glVertex2f(x, y)
            gl.glEnd()
