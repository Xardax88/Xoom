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
├── main.py                 # Punto de entrada principal
├── settings.py            # Configuración global
├── requirements.txt       # Dependencias
├── assets/
│   └── maps/             # Archivos de mapas
│       └── test_map.txt  # Mapa de prueba
├── core/                 # Lógica del juego
│   ├── __init__.py
│   ├── game.py          # Clase principal del juego
│   ├── player.py        # Lógica del jugador
│   ├── map_loader.py    # Cargador de mapas
│   └── bsp_tree.py      # Árbol de partición binaria
├── render/               # Sistema de renderizado
│   ├── __init__.py
│   ├── renderer.py      # Renderizador principal
│   └── minimap.py       # Renderizado del minimapa
└── utils/                # Utilidades
    ├── __init__.py
    ├── logger.py        # Sistema de logging
    └── math_utils.py    # Utilidades matemáticas
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
# Cada línea define un polígono: x1,y1 x2,y2 x3,y3 x4,y4

# Polígonos en sentido horario = paredes interiores (sólidas)
200,150 350,150 350,250 200,250

# Polígonos en sentido anti-horario = áreas exteriores
50,50 950,50 950,650 50,650
```

## Principios SOLID Aplicados

1. **Single Responsibility**: Cada clase tiene una responsabilidad específica
   - `Player`: Maneja solo la lógica del jugador
   - `MapLoader`: Solo carga mapas
   - `Renderer`: Solo renderiza
   
2. **Open/Closed**: Extensible sin modificar código existente
   - Interfaces para `ILogger`, `IRenderer`, `IMapLoader`
   
3. **Liskov Substitution**: Las implementaciones pueden reemplazar sus interfaces
   
4. **Interface Segregation**: Interfaces específicas y pequeñas
   
5. **Dependency Inversion**: Dependencias a través de interfaces

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

## Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request