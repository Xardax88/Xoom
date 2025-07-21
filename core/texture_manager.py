from pathlib import Path
from PIL import Image
import settings

from OpenGL.GL import (
    glGenTextures,
    glBindTexture,
    glTexImage2D,
    glTexParameteri,
    GL_TEXTURE_2D,
    GL_RGBA,
    GL_UNSIGNED_BYTE,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_LINEAR,
    GL_LINEAR_MIPMAP_LINEAR,
    GL_REPEAT,
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
        img = self.get_texture(name)
        logger.debug(f"Textura {name} cargada desde disco")
        tex_id = glGenTextures(1)
        logger.debug(f"Cargando textura: {name}")
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        logger.debug(f"Textura subida a OpenGL con ID: {tex_id}")
        self._gl_ids[name] = tex_id
        return tex_id