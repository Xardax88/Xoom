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
import logging

import settings
from logging_setup import configure_logging

from core.map_loader import FileMapLoader
from core.bsp import BSPBuilder
from core.player import Player
from core.game import Game
from render.pygame_renderer import PygameRenderer

logger = logging.getLogger(__name__)


def run() -> None:
    configure_logging()
    logger.info("Iniciando Xoom...")

    # 1. Cargar mapa
    loader = FileMapLoader()
    map_data = loader.load(settings.DEFAULT_MAP_FILE)
    logger.info("Mapa cargado: %s segmentos", len(map_data.segments))

    # 2. Construir BSP
    bsp_builder = BSPBuilder(
        max_depth=settings.BSP_MAX_DEPTH, strategy=settings.BSP_SPLIT_STRATEGY
    )
    bsp_root = bsp_builder.build(map_data.segments)
    logger.info("BSP construido.")

    # 3. Inicializar jugador
    player = Player(
        x=settings.PLAYER_START_X,
        y=settings.PLAYER_START_Y,
        angle_deg=settings.PLAYER_START_ANGLE_DEG,
        fov_deg=settings.PLAYER_FOV_DEG,
        fov_length=settings.PLAYER_FOV_LENGTH,
    )

    # 4. Renderer
    renderer = PygameRenderer(
        width=settings.WINDOW_WIDTH,
        height=settings.WINDOW_HEIGHT,
        fps=settings.FPS_TARGET,
        scale=settings.MINIMAP_SCALE,
        margin=settings.MINIMAP_MARGIN,
        color_theme=settings.COLOR_THEME,
    )

    # 5. Game loop
    game = Game(map_data=map_data, bsp_root=bsp_root, player=player, renderer=renderer)
    game.run()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nSaliendo...")
        sys.exit(0)
