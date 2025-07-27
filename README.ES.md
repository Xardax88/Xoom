[Inglish 🇺🇸](README.md) /
[Español 🇦🇷](README.ES.md)
# Xoom - Motor Estilo Doom en Python 🐍

Un motor de juego 3D estilo "raycasting" inspirado en clásicos como Doom, implementado en Python y OpenGL.

[![Estado del Proyecto](https://img.shields.io/badge/status-en%20desarrollo-indigo)](https://github.com/Xardax88/Xoom)
[![Último Commit](https://img.shields.io/github/last-commit/Xardax88/Xoom)](https://github.com/Xardax88/Xoom/commits/main)
[![Tamaño del Repo](https://img.shields.io/github/repo-size/Xardax88/Xoom)](https://github.com/Xardax88/Xoom)
[![Licencia](https://img.shields.io/github/license/Xardax88/Xoom)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![Xoom Demo GIF](/docs/gameplay.gif)

## Acerca del Proyecto

**Xoom** es un viaje personal para recrear la magia de los shooters en primera persona de los 90 como Doom y Duke Nukem 3D. 
Este proyecto utiliza técnicas de renderizado 2.5D usando mapas basados en polígonos 2D para construir los niveles, que luego se representan con render 3D.

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
- [Agradecimientos](#agradecimientos)

### Características Principales

- **Carga de Mapas por Vectores**: Los niveles se definen mediante vertices agrupados en sectores, en archivos de texto simple.
- **Árbol BSP**: Se utiliza la Partición Binaria del Espacio para una gestión y renderizado eficiente de la geometría del mapa.
- **Renderizado 3D**: Proyección de un mapa 2D a un entorno 3D.
- **Sistema de Colisiones**: Detección de colisiones entre el jugador el entorno.
- **Shaders Modernos**: Uso de GLSL para el pipeline de renderizado.
- **Iluminación Dinámica**: Implementación de iluminación dinámica para mejorar la inmersión.
- **Logging Detallado**: Registro de eventos, desde la carga de mapas hasta errores de renderizado, para facilitar la depuración.

### Construido Con

Este proyecto ha sido posible gracias a las siguientes tecnologías:

![Python 3.11+](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![PyOpenGL](https://img.shields.io/badge/PyOpenGL-8DD6F9?style=for-the-badge&logo=opengl&logoColor=black)
![GLFW](https://img.shields.io/badge/GLFW-FF0000?style=for-the-badge&logo=glfw&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-30B8D9?style=for-the-badge&logo=pillow&logoColor=white)
![PyGame](https://img.shields.io/badge/PyGame-000000?style=for-the-badge&logo=pygame&logoColor=white)

![Tidal](https://img.shields.io/badge/Tidal-000000?style=for-the-badge&logo=tidal&logoColor=white)
![Fedora](https://img.shields.io/badge/Fedora-294172?style=for-the-badge&logo=fedora&logoColor=white)
![Windows 11](https://img.shields.io/badge/Windows%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)

![PyCharm](https://img.shields.io/badge/PyCharm-000000?style=for-the-badge&logo=pycharm&logoColor=white)
![Photoshop](https://img.shields.io/badge/Photoshop-31A8FF?style=for-the-badge&logo=photoshop&logoColor=white)
![Blender](https://img.shields.io/badge/Blender-F5792A?style=for-the-badge&logo=blender&logoColor=white)

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

2.  Crea un entorno virtual para evitar conflictos con otras dependencias de Python:
   - En Windows:
       ```bash
       python -m venv venv
       venv\Scripts\activate
       ```
    
   - En Linux/MacOS:
       ```bash
       python3 -m venv venv
       source venv/bin/activate
       ```

3.  Ejecuta el script para instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4.  Ejecuta el juego:
   - En Windows:
       ```bash
       python main.py
       ```
   - En Linux/MacOS:
       ```bash
       python3 main.py
       ```

### Controles

En el juego
- W: Mover adelante
- S: Mover atrás
- A: Girar a la izquierda
- D: Girar a la derecha
- Q: Desplazamiento lateral (strafe) a la izquierda
- E: Desplazamiento lateral (strafe) a la derecha
- ESC: Salir del juego

En el menú principal
- Enter: Seleccionar opción
- Esc: Salir del juego
- ↑: Subir opción
- ↓: Bajar opción
- ←: No implementado
- →: No implementado

### Roadmap

- [x] Carga de mapas desde archivos .xmap
- [x] Construcción de Árbol BSP
- [x] Renderizado 3D de paredes
  - [x] Renderizado mediante shaders GLSL con texturas
  - [x] Aplicar texturas a las paredes
- [x] Sistema de iluminación dinámica
- [x] Movimiento y colisiones del jugador
- [x] Renderizado mediante shaders GLSL con texturas
- [x] Menú principal basico
- [x] Editor de mapas básico (Aún está en desarrollo)
- [x] Implementar sectores "Portal" 
- [ ] Sistema de puertas
- [ ] Implementar texturas por vertices
- [ ] Implementar sprites para enemigos y objetos
  - [ ] Actualizar a modelos 3D
- [ ] Implementar un sistema de partículas
- [ ] Añadir efectos de sonido y música
- [ ] Portar el renderizado a Vulkan

Consulta los issues abiertos para una lista completa de las características propuestas (y errores conocidos).

### Formato de Mapas

```
# Formato del XMAP:
# El # indica un comentario y es ignorado por el parser.
#
SECTOR <floor_h> <ceil_h>
    TEXTURES <texture_wall> <texture_floor(optional)> <texture_ceil(optional)>
    <cord_x> <cord_y>
    <cord_x> <cord_y>
    ...
END

# Cada sector de define por un SECTOR, y termina en un END, y contiene:
# floor_h: Altura del suelo del sector
# ceil_h: Altura del techo del sector
# cord_x, cord_y : Coordenadas del vertice
# Una sub seccion TEXTURES que tiene las texturas del sector, donde:
# texture_wall: Textura de las paredes del sector
# texture_floor: Textura del suelo del sector y si no se especifica, se usa la textura de la pared
# texture_ceil: Textura del techo del sector y si no se especifica, se usa la textura de la pared

PLAYER_START <x> <y> <ang>
# x, y: Posición inicial del jugador
# ang: Ángulo inicial del jugador (en grados)
```

## Licencia

Distribuido bajo la Licencia MIT. Consulta [LICENSE](LICENSE) para más información.

## Contacto
- [Xardax88](https://github.com/Xardax88) (Paragoni Maximiliano) - [@Xardax88](https://twitter.com/Xardax88)
- Enlace del Proyecto: https://github.com/Xardax88/Xoom

## Agradecimientos
- A id Software por crear el legendario DOOM y ser una fuente inagotable de inspiración.
- A la comunidad de El Diagrama por su apoyo y motivación constante.
- A todos los que han contribuido con ideas y sugerencias para mejorar este proyecto.
- A los desarrolladores de las bibliotecas y herramientas utilizadas en este proyecto.
- A ti, por interesarte en este proyecto y por tu apoyo.