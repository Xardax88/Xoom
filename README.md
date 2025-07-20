# Xoom - Motor Estilo Doom en Python

Un motor de juego 3D estilo Doom implementado en Python.

![Status](https://img.shields.io/badge/status-En%20Desarrollo-blue)
![Tamaño del Repo](https://img.shields.io/github/repo-size/Xardax88/DiamiPyBot)
[![Licencia](https://img.shields.io/github/license/Xardax88/DiamiPyBot)](LICENSE)
![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=Black)](https://github.com/psf/black)
![PyGame Version](https://img.shields.io/badge/PyGame-2.6+-blue?logo=pygame&logoColor=white)
![SDL Version](https://img.shields.io/badge/SDL-2.28+-blue?logo=libsdl&logoColor=white)



## Características

- **Carga de mapas por vectores**: Los mapas se definen como polígonos usando coordenadas 2D
- **Árbol BSP**: Partición binaria del espacio para renderizado eficiente
- **Minimapa en tiempo real**: Visualización del mapa y posición del jugador
- **Campo de visión (FOV)**: Representación visual del área que ve el jugador
- **Sistema de logging**: Registro completo de eventos y errores

## Estructura del Proyecto

```
Xoom/
├─ assets/
│  ├─ maps/
│  │  └─ E1M1.xmap
├─ core/
│  ├─ __init__.py
│  ├─ bsp.py
│  ├─ collision.py
│  ├─ errors.py
│  ├─ game.py
│  ├─ map_data.py
│  ├─ map_loader.py
│  ├─ match_utils.py
│  ├─ player.py
│  ├─ types.py
│  └─ visibility.py
├─ logs/
├─ render/
│  ├─ __init__.py
│  ├─ camera.py
│  ├─ colors.py
│  ├─ pygame_renderer.py
│  └─ renderer_base.py
├─ settings.py
├─ logging_setup.py
├─ main.py
└─ requirements.txt
```

## Instalación

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `python main.py`

## Controles

- **W/↑**: Mover adelante
- **S/↓**: Mover atrás  
- **A/←**: Girar izquierda
- **D/→**: Girar derecha
- **ESC**: Salir

## Formato de Mapas

Los mapas se definen en archivos de texto con el siguiente formato:

```
# Comentarios empiezan con #
# Los polígonos se definen con coordenadas X Y por cada vértice
# POLY <nombre>
# Define un polígono con un nombre específico
# Las coordenadas son en el formato X Y
# El polígono termina con END
# El poligono puede tener mas de 4 vértices
#
# SEG <nombre>
# Define un segmento de línea con un nombre específico
# Las coordenadas son en el formato X Y
# El segmento termina con END
#
# PLAYER_START Defines la posición inicial del jugador

# Polígonos en sentido horario = paredes interiores (sólidas)
POLY column
-80 -20
20 -20
20 20
-20 20
END

# Polígonos en sentido anti-horario = áreas exteriores
POLY wall
-100 100
100 100
100 -100
-100 -100
END
```

## Configuración

Todas las configuraciones se encuentran en `settings.py`:

- Resolución de pantalla
- FPS objetivo
- Velocidad del jugador
- Colores y estilos
- Configuración de logging

## Logging

El sistema registra automáticamente:

- Carga de mapas y errores
- Construcción del árbol BSP
- Eventos de inicialización
- Errores de renderizado

Los logs se guardan en la carpeta `logs/` con timestamp diario.

## Próximas Características

- Renderizado 3D completo
- Texturas en paredes
- Detección de colisiones
- Efectos de iluminación
- Soporte para sprites
- Audio espacial