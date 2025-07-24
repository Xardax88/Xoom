[Inglish 🇺🇸](README) /
[Español 🇦🇷](README_ES)
# Xoom - Motor Estilo Doom en Python 🐍

Un motor de juego 3D estilo "raycasting" inspirado en clásicos como Doom, implementado en Python y OpenGL.

[![Estado del Proyecto](https://img.shields.io/badge/status-en%20desarrollo-indigo)](https://github.com/Xardax88/Xoom)
[![Último Commit](https://img.shields.io/github/last-commit/Xardax88/Xoom)](https://github.com/Xardax88/Xoom/commits/main)
[![Tamaño del Repo](https://img.shields.io/github/repo-size/Xardax88/Xoom)](https://github.com/Xardax88/Xoom)
[![Licencia](https://img.shields.io/github/license/Xardax88/Xoom)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- **Añade aquí una captura o un GIF del proyecto en acción** -->
<!-- ![Xoom Demo GIF](URL_DEL_GIF_AQUI) -->

## Acerca del Proyecto

**Xoom** es un viaje personal para recrear la magia de los shooters en primera persona de los 90 como Doom y Duke Nukem 3D. 
Este proyecto utiliza técnicas de renderizado 2.5D (raycasting sobre un mapa 2D) y un sistema de mapas basado en polígonos para construir los niveles.

Nació de la nostalgia y el desafío. Hace años, desarrollé un motor similar en C++, pero el código se perdió en el tiempo.
Este es mi intento de reconstruirlo desde cero, aplicando nuevos conocimientos, esta vez en Python, y documentando cada paso en GitHub.

El objetivo a largo plazo es no solo revivir esa experiencia de juego, sino también utilizar este proyecto como un campo de pruebas para aprender la API de Vulkan, planeando una futura migración del renderizador.

## Tabla de Contenido
- [Acerca del Proyecto](#acerca-del-proyecto)
- [Características Principales](#características-principales)
- [Construido Con](#construido-con)
- [Empezando](#empezando)
- [Controles](#controles)
- [Roadmap](#roadmap)
- [Formato de Mapas](#formato-de-mapas)
- [Licencia](#licencia)
- [Contacto](#contacto)
- [Contribuir](#contribuir)

### Características Principales

-   **Carga de Mapas por Vectores**: Los niveles se definen mediante polígonos y segmentos en archivos de texto simples.
-   **Árbol BSP**: Se utiliza la Partición Binaria del Espacio para una gestión y renderizado eficiente de la geometría del mapa.
-   **Renderizado 3D**: Proyección de un mapa 2D a un entorno 3D, renderizando paredes con altura y perspectiva.
-   **Sistema de Colisiones**: Detección simple de colisiones entre el jugador y las paredes del entorno.
-   **Shaders Modernos**: Uso de GLSL para el pipeline de renderizado.
-   **Logging Detallado**: Registro de eventos, desde la carga de mapas hasta errores de renderizado, para facilitar la depuración.

### Construido Con

Este proyecto ha sido posible gracias a las siguientes tecnologías:

-   [Python 3.11+](https://www.python.org/)
-   [PyOpenGL](http://pyopengl.sourceforge.net/)
-   [GLFW](https://www.glfw.org/)
-   [NumPy](https://numpy.org/)
-   [Pillow](https://python-pillow.org/)

## Empezando

Sigue estos pasos para tener una copia local del proyecto funcionando.

### Prerrequisitos

Asegúrate de tener instalado Python 3.11 o una versión superior.

-   **Python 3.11+**

### Instalación

1.  Clona el repositorio en tu máquina local:
    ```bash
    git clone https://github.com/Xardax88/Xoom
    cd Xoom
    ```

2. Ejecuta el script de instalación para instalar las dependencias:
    ```bash
    python -m pip install -r requirements.txt
    ```

3. Ejecuta el juego:
    ```bash
    python main.py
    ```

### Controles

- W: Mover adelante
- S: Mover atrás
- A: Girar a la izquierda
- D: Girar a la derecha
- Q: Desplazamiento lateral (strafe) a la izquierda
- E: Desplazamiento lateral (strafe) a la derecha
- ESC: Salir del juego

### Roadmap

- [x] Carga de mapas desde archivos .xmap
- [x] Construcción de Árbol BSP
- [x] Renderizado 3D de paredes
  - [x] Renderizado mediante shaders GLSL
  - [x] Aplicar texturas a las paredes
- [x] Movimiento y colisiones del jugador
- [ ] Renderizar suelos y techos con texturas
- [ ] Implementar sprites para enemigos y objetos
- [ ] Sistema de iluminación (sectores con diferente brillo)
- [ ] Añadir efectos de sonido y música
- [ ] Portar el renderizador a Vulkan

Consulta los issues abiertos para una lista completa de las características propuestas (y errores conocidos).

### Formato de Mapas

Los mapas se definen en archivos .xmap. La sintaxis es simple y basada en texto.
- Comentarios: Cualquier línea que empiece con # es ignorada.
- PLAYER_START: Define la posición inicial X Y y el ángulo A del jugador.
- POLY: Define un polígono. La sintaxis es POLY <nombre> <textura> <altura>. 

Los vértices se listan a continuación, uno por línea, y se cierra con END.
- Los polígonos en sentido horario se consideran paredes interiores (Columnas).
- Los polígonos en sentido anti-horario definen áreas exteriores (Habitaciones).
- SEG: Define un segmento de línea (una pared individual). La sintaxis es SEG <nombre> <textura> <altura>.

## Licencia

Distribuido bajo la Licencia MIT. Consulta [LICENSE](LICENSE) para más información.

## Contacto
[Xardax88](https://github.com/Xardax88) (Paragoni Maximiliano) - [@Xardax88](https://twitter.com/Xardax88)

Enlace del Proyecto: https://github.com/Xardax88/Xoom