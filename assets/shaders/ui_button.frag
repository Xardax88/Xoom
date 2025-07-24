#version 330 core

// La salida del shader: el color final del fragmento (píxel)
out vec4 FragColor;

// Uniform: el color del botón que pasamos desde Python
uniform vec3 objectColor;

void main()
{
    // Asignamos el color del botón, con un canal alfa de 1.0 (opaco)
    FragColor = vec4(objectColor, 1.0);
}