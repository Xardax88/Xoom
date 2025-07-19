#########################################################################
# settings.py - Configuración global
#########################################################################

import os

# Configuración de pantalla
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Configuración del jugador
PLAYER_SPEED = 100  # pixels por segundo
PLAYER_ROTATION_SPEED = 180  # grados por segundo
PLAYER_FOV = 60  # grados
PLAYER_SIZE = 5  # radio en pixels

# Colores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Configuración del minimapa
MINIMAP_SCALE = 1
MINIMAP_POSITION = (10, 10)  # x, y desde la esquina superior izquierda

# Configuración de archivos
MAPS_DIR = os.path.join("assets", "maps")
LOGS_DIR = "logs"

# Configuración de logging
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
