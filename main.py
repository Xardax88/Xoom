#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
## Xoom - A Doom like game engine
#########################################################################
## License: MIT License
#########################################################################
## Author: Xardax
## Date: 2025-06-19
## Version: 0.1.0
## Python Version: 3.11
## Description:
##      This is the main entry point for the Xoom game engine.
#########################################################################

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from utils.logger import get_logger


def main():
    """Función principal"""
    logger = get_logger()
    logger.info("=== Iniciando Xoom ===")

    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        logger.info("Juego interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        sys.exit(1)

    logger.info("=== Xoom terminado ===")


if __name__ == "__main__":
    main()
