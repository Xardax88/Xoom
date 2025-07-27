"""
Dibuja una cuadrícula de ayuda para el diseño de mapas.
"""

import OpenGL.GL as gl


class Grid:
    """
    Dibuja una cuadrícula de ayuda para el canvas del editor.
    """

    def __init__(self, cell_size: int, width: int, height: int):
        self.cell_size = cell_size
        self.width = width
        self.height = height

    def draw(self):
        """
        Dibuja la cuadrícula usando líneas OpenGL.
        """
        gl.glColor3f(0.4, 0.4, 0.4)
        gl.glBegin(gl.GL_LINES)
        # Líneas verticales
        for x in range(0, self.width, self.cell_size):
            gl.glVertex2f(x, 40)
            gl.glVertex2f(x, self.height + 40)
        # Líneas horizontales
        for y in range(40, self.height + 40, self.cell_size):
            gl.glVertex2f(0, y)
            gl.glVertex2f(self.width, y)
        gl.glEnd()
