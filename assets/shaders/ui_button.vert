#version 460 core
// Atributo de entrada: la posición 2D del vértice de nuestro quad
layout (location = 0) in vec2 aPos;
// Uniforms: matrices que vienen desde Python
uniform mat4 model;
uniform mat4 projection;
void main() {
    // La posición final es el resultado de escalar/mover el quad y luego proyectarlo
    gl_Position = projection * model * vec4(aPos, 0.0, 1.0);
}