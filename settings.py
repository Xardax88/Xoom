"""
settings.py

Configuraciones globales del proyecto Xoom.

Edita estos valores para ajustar la ventana, FPS, archivo de mapa, FOV del jugador, etc.
"""

from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
MAPS_DIR = ASSETS_DIR / "maps"
LOGS_DIR = BASE_DIR / "logs"

# Archivo de mapa por defecto
DEFAULT_MAP_FILE = MAPS_DIR / "E1M1.xmap"

# --- Ventana / Render ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS_TARGET = 60

# Escala del minimapa (pixeles por unidad de mapa)
MINIMAP_SCALE = 2.0  # 1 unidad del mapa = 4 px

# Margen del minimapa dentro de la ventana
MINIMAP_MARGIN = 16

# Color theme override (puede dejarse None para defaults en renderer)
COLOR_THEME = None

# --- Jugador ---
PLAYER_START_X = -90.0
PLAYER_START_Y = 90.0
PLAYER_START_ANGLE_DEG = 0.0  # 0° = eje +X (derecha)
PLAYER_FOV_DEG = 60.0  # apertura total del FOV
PLAYER_FOV_LENGTH = 250.0  # longitud de las líneas de FOV en unidades de mapa
PLAYER_SPEED = 30.0  # unidades por segundo
PLAYER_TURN_SPEED_DEG = 5.0  # grados/seg

# --- Logging ---
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE_BASENAME = "xoom.log"
LOG_ROTATE_DAILY = True  # si True usa TimedRotatingFileHandler
LOG_BACKUP_COUNT = 7  # cuantos días conservar
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- BSP ---
BSP_MAX_DEPTH = 32  # seguridad para recursión
BSP_SPLIT_STRATEGY = "first"  # first | median | longest | random (para evolucionar)

# --- Input ---
ENABLE_MOUSE_LOOK = False  # placeholder para futuro
