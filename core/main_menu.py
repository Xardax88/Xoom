'''
Menu principal del juego. Permite al usuario seleccionar entre jugar o salir.
'''

from typing import Optional
from render.renderer_base import IRenderer

class MainMenu:
    def __init__(self, renderer: IRenderer):
        self.renderer = renderer
        self.selected_option = 0  # 0: Jugar, 1: Salir
        self.options = ["Jugar", "Salir"]

    def show(self) -> Optional[str]:
        while self.renderer.is_running():
            self.renderer.draw_main_menu(self.options, self.selected_option)
            self.renderer.flip_buffers()
            self.renderer.dispatch_events()
            inp = self.renderer.poll_input()
            if inp.get("down"):
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif inp.get("up"):
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif inp.get("select"):
                return self.options[self.selected_option]
            elif inp.get("quit"):
                return "Salir"
        return None