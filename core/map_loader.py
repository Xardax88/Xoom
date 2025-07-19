#########################################################################
# core/map_loader.py - Cargador de mapas
#########################################################################

from abc import ABC, abstractmethod
from typing import List
from utils.math_utils import Vector2D, MathUtils
from utils.logger import get_logger


class IMapLoader(ABC):
    """Interface para cargadores de mapas"""

    @abstractmethod
    def load_map(self, filepath: str) -> List[List[Vector2D]]:
        pass


class MapLoader(IMapLoader):
    """Cargador de mapas desde archivos de texto"""

    def __init__(self):
        self.logger = get_logger()

    def load_map(self, filepath: str) -> List[List[Vector2D]]:
        """
        Cargar mapa desde archivo
        Formato esperado: cada línea representa un polígono con coordenadas x1,y1 x2,y2 x3,y3...
        """
        try:
            polygons = []

            with open(filepath, "r") as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith(
                        "#"
                    ):  # Ignorar líneas vacías y comentarios
                        continue

                    vertices = self._parse_line(line, line_num)
                    if (
                        vertices and len(vertices) >= 3
                    ):  # Al menos 3 vértices para un polígono
                        polygons.append(vertices)

                        # Log información sobre la orientación
                        is_clockwise = MathUtils.is_clockwise(vertices)
                        orientation = (
                            "horario (interior)"
                            if is_clockwise
                            else "anti-horario (exterior)"
                        )
                        self.logger.debug(
                            f"Polígono {len(polygons)}: {len(vertices)} vértices, orientación {orientation}"
                        )

            self.logger.info(
                f"Mapa cargado exitosamente: {len(polygons)} polígonos desde {filepath}"
            )
            return polygons

        except FileNotFoundError:
            self.logger.error(f"Archivo de mapa no encontrado: {filepath}")
            return []
        except Exception as e:
            self.logger.error(f"Error cargando mapa {filepath}: {str(e)}")
            return []

    def _parse_line(self, line: str, line_num: int) -> List[Vector2D]:
        """Parsear una línea del archivo de mapa"""
        try:
            coordinates = line.split()
            vertices = []

            for coord in coordinates:
                if "," in coord:
                    x_str, y_str = coord.split(",")
                    x, y = float(x_str), float(y_str)
                    vertices.append((x, y))
                else:
                    self.logger.warning(
                        f"Formato inválido en línea {line_num}: {coord}"
                    )

            return vertices

        except ValueError as e:
            self.logger.error(f"Error parseando línea {line_num}: {str(e)}")
            return []
