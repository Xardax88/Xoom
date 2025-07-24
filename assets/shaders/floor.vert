#version 330 core

// Atributos de entrada desde el VBO
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoordIn; // <-- NUEVO: Coordenadas de textura

// Uniforms: matrices que vienen desde el código Python
uniform mat4 modelview;
uniform mat4 projection;

// Salida hacia el fragment shader
out vec2 texCoord; // <-- NUEVO: Pasar UVs al fragment shader

void main()
{
    // La posición final en pantalla es el resultado de aplicar las transformaciones
    gl_Position = projection * modelview * vec4(position, 1.0);

    // Pasamos las coordenadas de textura directamente
    texCoord = texCoordIn;
}