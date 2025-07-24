"""
UI Renderer for GLFW OpenGL Application
"""

from OpenGL.GL import *


class UIRenderer:
    def __init__(self, renderer):
        self.renderer = renderer  # Referencia al GLFWOpenGLRenderer

    def draw_main_menu(self, options, selected_index):
        # Dibuja el menú principal con botones y selección
        # Usa OpenGL para dibujar los botones y resaltar el seleccionado

        width, height = self.renderer.width, self.renderer.height
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Parámetros de los botones
        btn_w, btn_h = 300, 60
        spacing = 40
        start_y = height // 2 + btn_h

        for i, opt in enumerate(options):
            x = (width - btn_w) // 2
            y = start_y - i * (btn_h + spacing)
            if i == selected_index:
                glColor3f(1.0, 1.0, 1.0)  # Blanco
            else:
                glColor3f(0.5, 0.5, 0.5)  # Gris

            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + btn_w, y)
            glVertex2f(x + btn_w, y - btn_h)
            glVertex2f(x, y - btn_h)
            glEnd()
