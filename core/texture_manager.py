"""
TextureManager: Módulo para gestionar texturas en OpenGL.
Carga texturas desde disco y las almacena en caché.
Utiliza PIL para manejar imágenes y OpenGL para subirlas como texturas.
"""

from pathlib import Path
from PIL import Image
import settings

from OpenGL.GL import *
from OpenGL.GL import glGetFloatv
from OpenGL.GL.EXT.texture_filter_anisotropic import (
    GL_TEXTURE_MAX_ANISOTROPY_EXT,
    GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT,
)

import logging

logger = logging.getLogger(__name__)


class TextureManager:
    """
    Gestiona la carga y caché de texturas.
    """

    def __init__(self, texture_dir: Path = settings.TEXTURE_DIR):
        self.texture_dir = texture_dir
        self._cache = {}
        self._gl_ids = {}

    def get_texture(self, name: str):
        """
        Devuelve la textura (como objeto PIL.Image) correspondiente al nombre.
        Si no está cargada, la carga desde disco.
        """
        if name in self._cache:
            return self._cache[name]
        path = self.texture_dir / f"{name}.png"
        if not path.exists():
            raise FileNotFoundError(f"Textura no encontrada: {path}")
        img = Image.open(path).convert("RGBA")
        self._cache[name] = img
        return img

    def clear_cache(self):
        """Limpia la caché de texturas."""
        self._cache.clear()
        self._gl_ids.clear()

    def get_gl_texture_id(self, name: str):
        if name is None:
            return None

        if name in self._gl_ids:
            return self._gl_ids[name]

        # Cargar la textura desde el disco
        img = self.get_texture(name)
        tex_id = glGenTextures(1)
        logger.debug(f"Cargando textura: {name}")
        glBindTexture(GL_TEXTURE_2D, tex_id)

        # Subir la textura a OpenGL
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            img.width,
            img.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img.tobytes(),
        )

        # Configurar parámetros de la textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Generar mipmaps
        glGenerateMipmap(GL_TEXTURE_2D)

        # Aplicar filtrado anisotrópico
        max_aniso = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, max_aniso)

        logger.debug(f"Textura subida a OpenGL con ID: {tex_id}")
        self._gl_ids[name] = tex_id
        return tex_id
