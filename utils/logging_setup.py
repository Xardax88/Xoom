"""
logging_setup.py

Configura el sistema de logging del proyecto con parámetros definidos en settings.py.
Genera el directorio de logs si no existe.

Uso:
    from logging_setup import configure_logging
    configure_logging()

Luego usa logging.getLogger(__name__) en tus módulos.
"""

import logging
from pathlib import Path
import settings

_CONFIGURED = False


def configure_logging(force: bool = False) -> None:
    """
    Configura el logging para que el archivo de log se sobrescriba en cada inicio.
    Elimina cualquier rotación y asegura que el archivo se borre y se cree de nuevo.
    """
    global _CONFIGURED
    if _CONFIGURED and not force:
        return

    log_dir: Path = settings.LOGS_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / settings.LOG_FILE_BASENAME

    # El modo 'w' sobrescribe el archivo de log cada vez que se inicia el programa.
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")

    # También salida a consola
    console_handler = logging.StreamHandler()

    # Configuración básica del logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=settings.LOG_FORMAT,
        datefmt=settings.DATE_FORMAT,
        handlers=[file_handler, console_handler],
        force=True,  # asegura reconfiguración
    )
    _CONFIGURED = True
