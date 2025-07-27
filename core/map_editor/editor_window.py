"""
Ventana principal del editor de mapas.
Permite dibujar sectores sobre un canvas y gestionar archivos .xmap mediante un menú.
"""

import sys
import os

# Permite ejecutar este archivo directamente o como parte de un paquete
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from OpenGL.GL import *

from core.map_editor.grid import Grid
from core.map_editor.sector_drawer import SectorDrawer
from core.map_editor.map_data import MapData
from core.map_editor.menu_bar import MenuBar


class MapEditorWindow:
    """
    Clase principal para la ventana del editor de mapas.
    Gestiona la inicialización, el bucle principal, el menú y la interacción con el usuario.
    """

    def __init__(self, width=1000, height=700):
        self.width = width
        self.height = height
        self.running = False
        self.grid = Grid(
            cell_size=20, width=width, height=height - 40
        )  # Deja espacio para el menú
        self.map_data = MapData()
        self.sector_drawer = SectorDrawer(self.map_data, offset_y=40)
        self.menu_bar = MenuBar(self, width, 40)  # Menú superior de 40px de alto

    def run(self):
        """
        Inicia el bucle principal del editor.
        """
        pygame.init()
        pygame.display.set_caption("Xoom Map Editor")
        pygame.display.set_mode(
            (self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF
        )
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        self.running = True

        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()

        pygame.quit()

    def handle_events(self):
        """
        Maneja los eventos de entrada del usuario.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.pos[1] < 40:
                self.menu_bar.handle_event(event)
            else:
                self.sector_drawer.handle_event(event)

    def render(self):
        """
        Renderiza el menú, la cuadrícula y los sectores actuales.
        """
        glClear(GL_COLOR_BUFFER_BIT)
        self.menu_bar.draw()
        self.grid.draw()
        self.sector_drawer.draw()

    def load_map(self, filepath):
        """
        Carga un archivo .xmap y actualiza los datos del mapa.
        """
        self.map_data.load_from_xmap(filepath)

    def save_map(self, filepath):
        """
        Guarda el mapa actual en formato .xmap.
        """
        self.map_data.save_to_xmap(filepath)

    def undo_last_sector(self):
        """
        Elimina el último sector agregado al mapa.
        """
        self.map_data.remove_last_sector()


# Permite ejecutar el editor de forma independiente
if __name__ == "__main__":
    editor = MapEditorWindow()
    editor.run()
