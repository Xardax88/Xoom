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
import logging.handlers
from pathlib import Path
import settings

_CONFIGURED = False


def configure_logging(force: bool = False) -> None:
    global _CONFIGURED
    if _CONFIGURED and not force:
        return

    log_dir: Path = settings.LOGS_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / settings.LOG_FILE_BASENAME

    handlers = []
    if settings.LOG_ROTATE_DAILY:
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8",
            utc=False,
        )
    else:
        handler = logging.FileHandler(log_file, encoding="utf-8")
    handlers.append(handler)

    # También salida a consola
    console = logging.StreamHandler()
    handlers.append(console)

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=settings.LOG_FORMAT,
        datefmt=settings.DATE_FORMAT,
        handlers=handlers,
        force=True,  # asegura reconfiguración
    )
    _CONFIGURED = True
