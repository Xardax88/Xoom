[English 🇺🇸](README.md) /
[Español 🇦🇷](README.ES.md)

# Xoom - Doom-Style Engine in Python 🐍

A 3D "raycasting" game engine inspired by classics like Doom, implemented in Python and OpenGL.

[![Project Status](https://img.shields.io/badge/status-in%20development-indigo)](https://github.com/Xardax88/Xoom)
[![Last Commit](https://img.shields.io/github/last-commit/Xardax88/Xoom)](https://github.com/Xardax88/Xoom/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/Xardax88/Xoom)](https://github.com/Xardax88/Xoom)
[![License](https://img.shields.io/github/license/Xardax88/Xoom)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- ![Xoom Demo GIF](/docs/gameplay.gif) -->

## About the Project

**Xoom** is a personal journey to recreate the magic of 90s first-person shooters like Doom and Duke Nukem 3D.
This project uses 2.5D rendering techniques with polygon-based maps to build levels, rendered in 3D.

Born from nostalgia and challenge, this is a reconstruction of a lost C++ engine, now rebuilt in Python and documented step by step.

The long-term goal is to revive that gaming experience and use this project as a testbed for learning the Vulkan API, planning a future renderer migration.

## Table of Contents
- [About the Project](#about-the-project)
- [Main Features](#main-features)
- [Built With](#built-with)
- [Getting Started](#getting-started)
- [Controls](#controls)
- [Roadmap](#roadmap)
- [Map Format](#map-format)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

### Main Features

- **Vector-Based Map Loading**: Levels defined by vertices grouped in sectors, using simple text files.
- **BSP Tree**: Binary Space Partitioning for efficient geometry management and rendering.
- **3D Rendering**: Projects a 2D map into a 3D environment.
- **Collision System**: Player and environment collision detection.
- **Modern Shaders**: GLSL shaders for the rendering pipeline.
- **Dynamic Lighting**: Dynamic lighting implementation for immersion.
- **Detailed Logging**: Logs events from map loading to rendering errors for easier debugging.

### Built With

This project was made possible thanks to the following technologies:

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

## Getting Started

Follow these steps to get a local copy of the project running.

### Prerequisites

Make sure you have Python 3.11 or higher installed.

- **Python 3.11+**

### Installation

> **Recommendation:**  
> It is recommended to use a **virtual environment** to isolate project dependencies and avoid conflicts with other Python projects.

#### Create and activate a virtual environment

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

On Linux/MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

Once the virtual environment is activated, install dependencies and run the game as usual.

1. Clone the repository to your local machine:
    ```bash
    git clone https://github.com/Xardax88/Xoom
    cd Xoom
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the game:
   - On Windows:
       ```bash
       python main.py
       ```
   - On Linux/MacOS:
       ```bash
       python3 main.py
       ```

### Controls

In-game
- W: Move forward
- S: Move backward
- A: Turn left
- D: Turn right
- Q: Strafe left
- E: Strafe right
- ESC: Exit the game

In the main menu
- Enter: Select option
- Esc: Exit the game
- ↑: Move up
- ↓: Move down
- ←: Not implemented
- →: Not implemented

### Roadmap

- [x] Load maps from .xmap files
- [x] BSP Tree construction
- [x] 3D wall rendering
  - [x] Rendering with GLSL shaders and textures
  - [x] Apply textures to walls
- [x] Dynamic lighting system
- [x] Player movement and collisions
- [x] Rendering with GLSL shaders and textures
- [x] Basic main menu
- [x] Basic map editor (in progress)
- [x] Implement "Portal" sectors
- [ ] Door system
- [ ] Per-vertex textures
- [ ] Sprites for enemies and objects
  - [ ] Upgrade to 3D models
- [ ] Particle system
- [ ] Add sound effects and music
- [ ] Port the renderer to Vulkan

Check the open issues for a complete list of proposed features (and known bugs).

### Map Format

```
# XMAP Format:
# Lines starting with # are comments and ignored by the parser.
#
SECTOR <floor_h> <ceil_h>
    TEXTURES <texture_wall> <texture_floor(optional)> <texture_ceil(optional)>
    <cord_x> <cord_y>
    <cord_x> <cord_y>
    ...
END

# Each sector is defined by SECTOR ... END and contains:
# floor_h: Sector floor height
# ceil_h: Sector ceiling height
# cord_x, cord_y: Vertex coordinates
# A TEXTURES subsection with the sector's textures, where:
# texture_wall: Wall texture for the sector
# texture_floor: Floor texture (if not specified, wall texture is used)
# texture_ceil: Ceiling texture (if not specified, wall texture is used)

PLAYER_START <x> <y> <ang>
# x, y: Player initial position
# ang: Player initial angle (in degrees)
```

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Contact

- [Xardax88](https://github.com/Xardax88) (Paragoni Maximiliano) - [@Xardax88](https://twitter.com/Xardax88)
- Project Link: https://github.com/Xardax88/Xoom

## Acknowledgements

- To id Software for creating the legendary DOOM and being an endless source of inspiration.
- To the El Diagrama community for their constant support and motivation.
- To everyone who contributed ideas and suggestions to improve this project.
- To the developers of the libraries and tools used in this project.
- To you, for your interest and support.

## Contributing

Contributions are welcome! Please open issues or pull requests.  
Follow the coding standards: Python 3.8+, use BLACK, and always apply SOLID, DRY, and OOP principles.
