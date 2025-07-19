#########################################################################
# utils/logger.py - Sistema de logging
#########################################################################

import logging
import os
from datetime import datetime
from abc import ABC, abstractmethod


class ILogger(ABC):
    """Interface para el sistema de logging siguiendo el principio de Segregación de Interfaces"""

    @abstractmethod
    def debug(self, message: str) -> None:
        pass

    @abstractmethod
    def info(self, message: str) -> None:
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        pass


class Logger(ILogger):
    """Implementación del sistema de logging"""

    def __init__(self, name: str = "Xoom"):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """Configurar el logger con handlers para archivo y consola"""
        from settings import LOG_LEVEL, LOG_TO_FILE, LOG_TO_CONSOLE, LOGS_DIR

        # Configurar nivel
        level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        self.logger.setLevel(level)

        # Crear directorio de logs si no existe
        if LOG_TO_FILE and not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Handler para archivo
        if LOG_TO_FILE:
            log_filename = os.path.join(
                LOGS_DIR, f"xoom_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(log_filename)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Handler para consola
        if LOG_TO_CONSOLE:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)


# Singleton para el logger global
_logger_instance = None


def get_logger() -> ILogger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance
