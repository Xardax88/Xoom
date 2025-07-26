"""
Este modulo define excepciones personalizadas para errores comunes en la carga de mapas y construcción de BSP.
Estas excepciones facilitan la identificación y manejo de errores específicos en el flujo del juego.
"""

class MapLoadError(Exception):
    pass

class BSPBuildError(Exception):
    pass