"""
Colores por defecto (R,G,B).
"""

WHITE = (255, 255, 255)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)


# Tema por defecto para minimap
def default_theme():
    return {
        "bg": BLACK,
        "wall_interior": WHITE,
        "wall_exterior": GRAY,
        "player": RED,
        "fov": YELLOW,
        "visible_wall": GREEN,
        "floor": DARK_GRAY,
    }
