[Inglish 🇺🇸](README.md) /
[Español 🇦🇷](README.ES.mdES)
# Xoom - Doom-Style Engine in Python 🐍

A 3D "raycasting" game engine inspired by classics like Doom, implemented in Python and OpenGL.

[![Project Status](https://img.shields.io/badge/status-in%20development-indigo)](https://github.com/Xardax88/Xoom)
[![Last Commit](https://img.shields.io/github/last-commit/Xardax88/Xoom)](https://github.com/Xardax88/Xoom/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/Xardax88/Xoom)](https://github.com/Xardax88/Xoom)
[![License](https://img.shields.io/github/license/Xardax88/Xoom)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- **Add here a screenshot or GIF of the project in action** -->
<!-- ![Xoom Demo GIF](URL_OF_GIF_HERE) -->

## About the Project

**Xoom** is a personal journey to recreate the magic of 90s first-person shooters like Doom and Duke Nukem 3D.
This project uses 2.5D rendering techniques (raycasting over a 2D map) and a polygon-based map system to build levels.

It was born out of nostalgia and challenge. Years ago, I developed a similar engine in C++, but the code was lost over time.
This is my attempt to rebuild it from scratch, applying new knowledge, this time in Python, and documenting every step on GitHub.

The long-term goal is not only to revive that gaming experience but also to use this project as a testbed to learn the Vulkan API, planning a future migration of the renderer.

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
- [Contributing](#contributing)

### Main Features

-   **Vector-Based Map Loading**: Levels are defined using polygons and segments in simple text files.
-   **BSP Tree**: Binary Space Partitioning is used for efficient map geometry management and rendering.
-   **3D Rendering**: Projects a 2D map into a 3D environment, rendering walls with height and perspective.
-   **Collision System**: Simple collision detection between the player and environment walls.
-   **Modern Shaders**: Uses GLSL for the rendering pipeline.
-   **Detailed Logging**: Logs events from map loading to rendering errors to facilitate debugging.

### Built With

This project was made possible thanks to the following technologies:

-   [Python 3.11+](https://www.python.org/)
-   [PyOpenGL](https://mcfletch.github.io/pyopengl/)
-   [GLFW](https://www.glfw.org/)
-   [NumPy](https://numpy.org/)
-   [Pillow](https://python-pillow.github.io/)

## Getting Started

Follow these steps to get a local copy of the project running.

### Prerequisites

Make sure you have Python 3.11 or higher installed.

-   **Python 3.11+**

### Installation

1.  Clone the repository to your local machine:
    ```bash
    git clone https://github.com/Xardax88/Xoom
    cd Xoom
    ```

2. Run the install script to install dependencies:
    ```bash
    python -m pip install -r requirements.txt
    ```

3. Run the game:
    ```bash
    python main.py
    ```

### Controls

- W: Move forward
- S: Move backward
- A: Turn left
- D: Turn right
- Q: Strafe left
- E: Strafe right
- ESC: Exit the game

### Roadmap

- [x] Load maps from .xmap files
- [x] BSP Tree construction
- [x] 3D wall rendering
  - [x] Rendering with GLSL shaders
  - [x] Apply textures to walls
- [x] Player movement and collisions
- [ ] Render floors and ceilings with textures
- [ ] Implement sprites for enemies and objects
- [ ] Lighting system (sectors with different brightness)
- [ ] Add sound effects and music
- [ ] Port the renderer to Vulkan

Check the open issues for a complete list of proposed features (and known bugs).

### Map Format

Maps are defined in .xmap files. The syntax is simple and text-based.
- Comments: Any line starting with # is ignored.
- PLAYER_START: Defines the initial X Y position and angle A of the player.
- POLY: Defines a polygon. Syntax is POLY <name> <texture> <height>.

Vertices are listed below, one per line, and closed with END.
- Clockwise polygons are considered interior walls (Columns).
- Counterclockwise polygons define exterior areas (Rooms).
- SEG: Defines a line segment (an individual wall). Syntax is SEG <name> <texture> <height>.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Contact
[Xardax88](https://github.com/Xardax88) (Paragoni Maximiliano) - [@Xardax88](https://twitter.com/Xardax88)

Project Link: https://github.com/Xardax88/Xoom