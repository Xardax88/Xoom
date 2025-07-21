#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py

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
from render.texture_manager import TextureManager


logger = logging.getLogger(__name__)


def run() -> None:

    uname = platform.uname()

    # Configurar el logging
    configure_logging()
    # logger.info("Iniciando Xoom...")

    # Crear la ventana y el contexto de renderizado PRIMERO
    logger.info("Inicializando renderer y creando la ventana...")
    # Inicializar gestor de Texturas
    logger.info("Inicializando gestor de texturas...")
    texture_manager = TextureManager()
    texture_manager.load_texture(settings.DEFAULT_WALL_TEXTURE, "wall_placeholder")

    # Crear la ventana y el contexto de renderizado PRIMERO
    logger.info("Inicializando renderer y creando la ventana...")
    renderer = GLFW_OpenGLRenderer(
        width=settings.WINDOW_WIDTH,
        height=settings.WINDOW_HEIGHT,
        caption="Xoom Engine",
        texture_manager=texture_manager,  # Inyectar
        color_theme=settings.COLOR_THEME,
        scale=settings.MINIMAP_SCALE,
    )
    # logger.info("Renderer inicializado con éxito.")

    # Mostrar el Banner de inicio
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
    OpenGL: {renderer.get_opengl_version()}
    ==================================================
    Platform: {platform.system()} {platform.release()} ({platform.machine()})
    Processor: {uname.processor}
    ==================================================
    """
    )



    # Cargar los datos del mapa
    logger.info("Cargando datos del mapa...")
    loader = FileMapLoader()
    map_data = loader.load(settings.DEFAULT_MAP_FILE)
    logger.info("Mapa cargado: %s segmentos", len(map_data.segments))

    # Construir el árbol BSP a partir de los datos del mapa
    logger.info("Construyendo árbol BSP...")
    bsp_builder = BSPBuilder(
        max_depth=settings.BSP_MAX_DEPTH, strategy=settings.BSP_SPLIT_STRATEGY
    )
    bsp_root = bsp_builder.build(map_data.segments)
    logger.info("BSP construido con éxito.")

    # Inicializar al jugador usando la posición del mapa
    player = Player(
        x=map_data.player_start.x,
        y=map_data.player_start.y,
        angle_deg=settings.PLAYER_START_ANGLE_DEG,
        fov_deg=settings.PLAYER_FOV_DEG,
        fov_length=settings.PLAYER_FOV_LENGTH,
    )
    logger.info("Jugador inicializado en la posición: %s", player.pos)

    # Crear la instancia del juego con todos los componentes listos
    game = Game(map_data=map_data, bsp_root=bsp_root, player=player, renderer=renderer)

    # Iniciar el bucle principal del juego
    game.run()


if __name__ == "__main__":
    """
    Punto de entrada principal del juego.
    """
    try:
        run()
    except KeyboardInterrupt:
        print("\nSaliendo...")
        sys.exit(0)
    except Exception as e:
        logger.critical(
            "Error no controlado en el nivel superior: %s", e, exc_info=True
        )
        sys.exit(1)
