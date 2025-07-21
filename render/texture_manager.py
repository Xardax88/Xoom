"""
texture_manager.py

Gestor de recursos para texturas de OpenGL.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Dict, Optional

from OpenGL.raw.GL.EXT.texture_filter_anisotropic import GL_TEXTURE_MAX_ANISOTROPY_EXT
from PIL import Image
from OpenGL.GL import (
    glGenTextures,
    glBindTexture,
    glTexParameteri,
    glTexImage2D,
    glDeleteTextures,
    glTexParameterf,
    GL_TEXTURE_2D,
    GL_RGBA,
    GL_UNSIGNED_BYTE,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_REPEAT,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_MAG_FILTER,
    GL_LINEAR,
    GL_TEXTURE_MAX_ANISOTROPY,
)

logger = logging.getLogger(__name__)

@dataclass
class Texture:
    id: int
    width: int
    height: int


class TextureManager:
    def __init__(self):
        self._textures: Dict[str, Texture] = {}
        logger.info("Gestor de texturas inicializado.")

    def load_texture(self, path: Path, texture_name: Optional[str] = None) -> Texture:
        if not texture_name:
            texture_name = path.stem

        if texture_name in self._textures:
            logger.warning("La textura '%s' ya estaba cargada. Se reutilizará.", texture_name)
            return self._textures[texture_name]

        logger.info("Cargando textura '%s' desde %s", texture_name, path)
        try:
            img = Image.open(path).convert("RGBA")
            img_data = img.tobytes("raw", "RGBA", 0, -1)
        except IOError as e:
            logger.error("No se pudo cargar la textura: %s", e)
            raise

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        # Configuración de la textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Anisotropic filtering
        # if GL_TEXTURE_MAX_ANISOTROPY_EXT:
        #     max_aniso = glGetFloatv(GL_TEXTURE_MAX_ANISOTROPY_EXT)
        #     glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, max_aniso)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        texture = Texture(id=tex_id, width=img.width, height=img.height)
        self._textures[texture_name] = texture

        logger.debug("Textura '%s' cargada con ID %d", texture_name, tex_id)
        return texture

    def get_texture(self, name: str) -> Optional[Texture]:
        return self._textures.get(name)

    def unload_all(self) -> None:
        for texture_name, texture in self._textures.items():
            glDeleteTextures(1, [texture.id])
            logger.debug("Textura '%s' (ID: %d) liberada.", texture_name, texture.id)
        self._textures.clear()
        logger.info("Todas las texturas han sido liberadas.")


class Texture:
    """Contenedor simple para una textura de OpenGL."""

    def __init__(self, texture_id: int, width: int, height: int):
        self.id = texture_id
        self.width = width
        self.height = height


class TextureManager:
    """Carga, cachea y gestiona texturas de OpenGL."""

    def __init__(self):
        self._cache: Dict[Path, Texture] = {}
        logger.info("TextureManager inicializado.")

    def load_texture(self, path: Path) -> Texture:
        """
        Carga una textura desde un archivo. Si ya está cargada, la devuelve
        desde la caché.
        """
        if path in self._cache:
            return self._cache[path]

        logger.info("Cargando textura: %s", path)
        try:
            img = Image.open(path).convert("RGBA")
            img_data = img.tobytes("raw", "RGBA", 0, -1)
        except FileNotFoundError:
            logger.error("No se encontró el archivo de textura: %s", path)
            raise
        except Exception as e:
            logger.error("Fallo al cargar la imagen %s: %s", path, e)
            raise

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Configurar parámetros de la textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY, 16)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 16)

        # Subir los datos de la imagen a la GPU
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            img.width,
            img.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data,
        )

        texture = Texture(texture_id, img.width, img.height)
        self._cache[path] = texture
        logger.debug("Textura %s cargada con ID %d", path.name, texture_id)

        return texture

    def shutdown(self):
        """Libera todas las texturas de la GPU."""
        if self._cache:
            texture_ids = [tex.id for tex in self._cache.values()]
            glDeleteTextures(texture_ids)
            logger.info("Liberadas %d texturas de la GPU.", len(texture_ids))
        self._cache.clear()
