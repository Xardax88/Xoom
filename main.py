#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""main.py

Xoom - A Doom like game engine

Carga settings, configura logging, carga el mapa, construye el BSP y lanza el loop de render.

Author: Xardax
Date: 2025-06-19
Version: 0.1.0
"""

from __future__ import annotations

import sys
import platform
import logging

import settings
from utils.logging_setup import configure_logging
from core.map_loader import FileMapLoader
from core.bsp import BSPBuilder
from core.player import Player
from core.game import Game
from render.glfw_render import GLFW_OpenGLRenderer


logger = logging.getLogger(__name__)


class GameRunner:
    """
    Encapsula la lógica principal de inicialización y ejecución del juego.
    """

    def __init__(self) -> None:
        self.renderer = None
        self.map_data = None
        self.bsp_root = None
        self.player = None
        self.game = None

    def _initialize_renderer(self) -> None:
        """
        Inicializa el renderizador OpenGL con GLFW.
        """
        logger.info("Inicializando renderer y creando la ventana...")
        self.renderer = GLFW_OpenGLRenderer(
            width=settings.WINDOW_WIDTH,
            height=settings.WINDOW_HEIGHT,
            caption="Xoom Engine",
            color_theme=settings.COLOR_THEME,
            scale=settings.MINIMAP_SCALE,
        )
        # logger.info("Renderer inicializado con éxito.")

    def _load_map(self) -> None:
        """
        Carga los datos del mapa desde el archivo especificado en la configuración.
        """
        # logger.info("Cargando datos del mapa...")
        loader = FileMapLoader(texture_manager=self.renderer.texture_manager)
        self.map_data = loader.load(settings.DEFAULT_MAP_FILE)
        # logger.info("Mapa cargado: %s segmentos", len(self.map_data.segments))

    def _build_bsp_tree(self) -> None:
        """
        Construye el árbol BSP a partir de los datos del mapa cargados.
        """
        # logger.info("Construyendo árbol BSP...")
        bsp_builder = BSPBuilder(
            max_depth=settings.BSP_MAX_DEPTH, strategy=settings.BSP_SPLIT_STRATEGY
        )
        self.bsp_root = bsp_builder.build(self.map_data.segments)
        # logger.info("BSP construido con éxito.")

    def _initialize_player(self) -> None:
        """
        Inicializa al jugador con la posición inicial del mapa y la configuración.
        """
        self.player = Player(
            x=self.map_data.player_start.x,
            y=self.map_data.player_start.y,
            angle_deg=settings.PLAYER_START_ANGLE_DEG,
            fov_deg=settings.PLAYER_FOV_DEG,
            fov_length=settings.PLAYER_FOV_LENGTH,
        )
        logger.info("Jugador inicializado en la posición: %s", self.player.pos)

    def _create_game_instance(self) -> None:
        """
        Crea la instancia del juego con todos los componentes inicializados.
        """
        self.game = Game(
            map_data=self.map_data,
            bsp_root=self.bsp_root,
            player=self.player,
            renderer=self.renderer,
        )

    def _log_system_info(self) -> None:
        """
        Muestra información del sistema y versiones de las bibliotecas utilizadas.
        """
        uname = platform.uname()

        logger.info(
            f"""
        ==================================================
        Xoom - A Doom like game engine
        Author: Xardax
        Date relace: 2025-06-19
        Version: 0.1.0
        License: MIT
        ==================================================
        Python: {sys.version.split()[0]}
        GLFW: {GLFW_OpenGLRenderer.get_GLFW_version()}
        OpenGL: {self.renderer.get_opengl_version()}
        ==================================================
        Platform: {platform.system()} {platform.release()} ({platform.machine()})
        Processor: {uname.processor}
        ==================================================
        """
        )

    def run(self) -> None:
        """
        Ejecuta el juego, manejando la inicialización y el bucle principal.
        """
        try:
            # Configurar el logging
            configure_logging()

            self._initialize_renderer()
            self._log_system_info()
            self._load_map()
            self._build_bsp_tree()
            self._initialize_player()
            self._create_game_instance()

            # Iniciar el bucle principal del juego
            self.game.run()

        except Exception as e:
            logger.critical(
                "Error no controlado en el nivel superior: %s", e, exc_info=True
            )
            sys.exit(1)


if __name__ == "__main__":
    """
    Punto de entrada principal del juego.
    """
    try:
        game_runner = GameRunner()
        game_runner.run()
    except KeyboardInterrupt:
        print("\nSaliendo...")
        sys.exit(0)
