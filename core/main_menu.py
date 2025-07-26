"""
MainMenu: Menu principal del juego. Permite al usuario seleccionar entre jugar o salir.
"""

from typing import Optional
from render.renderer_base import IRenderer


class MainMenu:
    """
    Clase que gestiona el menú principal del juego, permitiendo al usuario navegar entre opciones
    y seleccionarlas. El desplazamiento por el menú se realiza solo una vez por pulsación de tecla,
    mejorando la experiencia de usuario y evitando saltos rápidos.
    """

    def __init__(self, renderer: IRenderer):
        self.renderer = renderer
        self.selected_option = 0  # 0: Jugar, 1: Salir
        self.options = ["Play", "Exit"]
        # Guarda el estado de las teclas en el frame anterior para detectar flancos de bajada
        self._last_input = {"up": False, "down": False, "select": False, "quit": False}

    def show(self) -> Optional[str]:
        """
        Muestra el menú principal y gestiona la navegación y selección de opciones.
        Solo permite mover la selección una vez por pulsación de tecla.
        """
        while self.renderer.is_running():
            self.renderer.draw_main_menu(self.options, self.selected_option)
            self.renderer.flip_buffers()
            self.renderer.dispatch_events()
            inp = self.renderer.poll_input()

            # Detectar flanco de bajada para cada tecla relevante
            down_pressed = inp.get("down", False) and not self._last_input.get(
                "down", False
            )
            up_pressed = inp.get("up", False) and not self._last_input.get("up", False)
            select_pressed = inp.get("select", False) and not self._last_input.get(
                "select", False
            )
            quit_pressed = inp.get("quit", False) and not self._last_input.get(
                "quit", False
            )

            if down_pressed:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif up_pressed:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif select_pressed:
                return self.options[self.selected_option]
            elif quit_pressed:
                return "Salir"

            # Actualizar el estado de las teclas para el siguiente frame
            self._last_input = {
                "up": inp.get("up", False),
                "down": inp.get("down", False),
                "select": inp.get("select", False),
                "quit": inp.get("quit", False),
            }
        return None
