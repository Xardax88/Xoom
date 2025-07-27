"""
Gestión de los datos del mapa y operaciones de carga/guardado en formato .xmap.
"""


class MapData:
    """
    Gestiona los sectores del mapa y la lógica de serialización/deserialización.
    """

    def __init__(self):
        self.sectors = []

    def add_sector(self, points):
        """
        Añade un nuevo sector al mapa.
        :param points: Lista de tuplas (x, y) que definen el polígono del sector.
        """
        self.sectors.append(points)

    def load_from_xmap(self, filepath):
        """
        Carga los sectores desde un archivo .xmap.
        """
        self.sectors.clear()
        with open(filepath, "r") as f:
            lines = f.readlines()
        sector = []
        in_sector = False
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("SECTOR"):
                in_sector = True
                sector = []
            elif line.startswith("END"):
                if sector:
                    self.sectors.append(sector)
                in_sector = False
            elif in_sector and not line.startswith("TEXTURES"):
                try:
                    x, y = map(float, line.split(","))
                    sector.append((x, y))
                except Exception:
                    continue

    def save_to_xmap(self, filepath):
        """
        Guarda los sectores actuales en formato .xmap.
        """
        with open(filepath, "w") as f:
            f.write("# Archivo generado por el editor de mapas\n")
            for sector in self.sectors:
                f.write("SECTOR 0 50\n")
                f.write(
                    "    TEXTURES wall_placeholder floor_placeholder ceiling_placeholder\n"
                )
                for x, y in sector:
                    f.write(f"    {int(x)} {int(y)}\n")
                f.write("END\n\n")

    def remove_last_sector(self):
        """
        Elimina el último sector agregado, si existe.
        """
        if self.sectors:
            self.sectors.pop()
