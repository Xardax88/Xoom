#########################################################################
# core/game.py - Clase principal del juego
#########################################################################

import pygame
import sys
from typing import List
from core.player import Player
from core.map_loader import MapLoader
from core.bsp_tree import BSPTree
from render.renderer import Renderer
from utils.math_utils import Vector2D
from utils.logger import get_logger


class Game:
    """Clase principal del juego que coordina todos los sistemas"""

    def __init__(self):
        self.logger = get_logger()
        self.renderer = None
        self.player = None
        self.map_loader = MapLoader()
        self.bsp_tree = BSPTree()
        self.polygons: List[List[Vector2D]] = []
        self.running = False
        self.delta_time = 0.0

    def initialize(self) -> bool:
        """Inicializar el juego"""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT

        self.logger.info("Inicializando Xoom...")

        # Inicializar renderizador
        self.renderer = Renderer(SCREEN_WIDTH, SCREEN_HEIGHT)
        if not self.renderer.initialize():
            return False

        # Inicializar jugador en el centro de la pantalla
        # self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 0.0)
        self.player = Player(80, 80, 0.0)

        # Cargar mapa de prueba
        self.load_test_map()

        self.logger.info("Xoom inicializado correctamente")
        return True

    def load_test_map(self) -> None:
        """Cargar un mapa de prueba"""
        import os
        from settings import MAPS_DIR

        # Crear directorio de mapas si no existe
        if not os.path.exists(MAPS_DIR):
            os.makedirs(MAPS_DIR)

        # Crear archivo de mapa de prueba si no existe
        test_map_path = os.path.join(MAPS_DIR, "E1M1.vex")
        if not os.path.exists(test_map_path):
            self._create_test_map(test_map_path)

        # Cargar el mapa
        self.polygons = self.map_loader.load_map(test_map_path)

        # Construir árbol BSP
        if self.polygons:
            self.bsp_tree.build_tree(self.polygons)

    def _create_test_map(self, filepath: str) -> None:
        """Crear un archivo de mapa de prueba"""
        test_map_content = """# Mapa de prueba para Xoom
# Formato: x1,y1 x2,y2 x3,y3 x4,y4 (polígonos)
# Sentido horario = interior, anti-horario = exterior

# Habitación exterior (anti-horario)
100,100 700,100 700,500 100,500

# Obstáculo interior 1 (horario)
200,150 300,150 300,200 200,200

# Obstáculo interior 2 (horario)
500,300 600,300 600,400 500,400"""

        with open(filepath, "w") as f:
            f.write(test_map_content)

        self.logger.info(f"Mapa de prueba creado: {filepath}")

    def handle_input(self) -> None:
        """Manejar entrada del usuario"""
        from settings import PLAYER_SPEED, PLAYER_ROTATION_SPEED

        # Eventos de pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Entrada de teclado
        keys = pygame.key.get_pressed()

        # Movimiento
        speed = 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            speed = PLAYER_SPEED
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            speed = -PLAYER_SPEED

        # Rotación
        rotation = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            rotation = -PLAYER_ROTATION_SPEED
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            rotation = PLAYER_ROTATION_SPEED

        # Aplicar movimiento al jugador
        self.player.set_movement(speed)
        self.player.set_rotation(rotation)

        # Salida con ESC
        if keys[pygame.K_ESCAPE]:
            self.running = False

    def update(self) -> None:
        """Actualizar lógica del juego"""
        self.player.update(self.delta_time)

    def render(self) -> None:
        """Renderizar el juego"""
        if self.renderer:
            # Obtener polígonos en orden de renderizado usando BSP
            ordered_polygons = self.bsp_tree.get_render_order(self.player.position)
            if not ordered_polygons:  # Fallback si BSP está vacío
                ordered_polygons = self.polygons

            self.renderer.render_frame(ordered_polygons, self.player)

    def run(self) -> None:
        """Loop principal del juego"""
        from settings import FPS

        if not self.initialize():
            self.logger.error("Error inicializando el juego")
            return

        self.running = True
        self.logger.info("Iniciando loop principal del juego")

        while self.running:
            self.delta_time = self.renderer.tick(FPS)

            self.handle_input()
            self.update()
            self.render()

        self.shutdown()

    def shutdown(self) -> None:
        """Cerrar el juego limpiamente"""
        if self.renderer:
            self.renderer.shutdown()
        self.logger.info("Xoom cerrado correctamente")
