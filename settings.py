"""
settings.py

Configuraciones globales del proyecto Xoom.

Edita estos valores para ajustar la ventana, FPS, archivo de mapa, FOV del jugador, etc.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
MAPS_DIR = ASSETS_DIR / "maps"
TEXTURE_DIR = ASSETS_DIR / "textures"
LOGS_DIR = BASE_DIR / "logs"

# Archivo de mapa por defecto
DEFAULT_MAP_FILE = MAPS_DIR / "E1M1.xmap"

# Textura
TEXTURE_SCALE = 50.0

# Ventana / Render
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS_TARGET = 60
MINIMAP_SCALE = 2.0
MINIMAP_MARGIN = 16
ENABLE_MINIMAP = True
COLOR_THEME = None

# Mapa
WALL_HEIGHT = 50.0

# Player
PLAYER_START_ANGLE_DEG = 0.0
PLAYER_FOV_DEG = 80.0
PLAYER_FOV_LENGTH = 500.0
PLAYER_SPEED = 40.0
PLAYER_TURN_SPEED_DEG = 60.0
PLAYER_HEIGHT = 18.0
PLAYER_COLLISION_RADIUS = 8.0

# Logging
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE_BASENAME = "xoom.log"
LOG_ROTATE_DAILY = True
LOG_BACKUP_COUNT = 1
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# BSP
BSP_MAX_DEPTH = 32  # seguridad para recursión
BSP_SPLIT_STRATEGY = "first"  # first | median | longest | random (para evolucionar)

# Input
ENABLE_MOUSE_LOOK = False  # placeholder para futuro
