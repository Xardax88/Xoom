#version 460 core
// Atributo de entrada: la posición 2D del vértice de nuestro quad
layout (location = 0) in vec2 aPos;
// Uniforms: matrices que vienen desde Python
uniform mat4 model;
uniform mat4 projection;

// Salida para el fragment shader
out vec2 TexCoord;

void main() {
    // La posición final es el resultado de escalar/mover el quad y luego proyectarlo
    gl_Position = projection * model * vec4(aPos, 0.0, 1.0);
    // El quad va de (0,0) a (1,1), así que usamos aPos directamente como coordenada de textura
    TexCoord = aPos;
}