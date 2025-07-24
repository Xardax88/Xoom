#version 330 core

// La salida del shader: el color final del fragmento (píxel)
out vec4 FragColor;

// Entrada desde el vertex shader
in vec2 texCoord;

// Uniforms desde Python
uniform sampler2D floorTexture; // <-- NUEVO: La textura del suelo
uniform vec3 floorColor;
uniform bool useTexture;        // <-- NUEVO: Flag para decidir qué dibujar

void main()
{
    if (useTexture) {
        // Si usamos textura, la leemos usando las coordenadas UV
        FragColor = texture(floorTexture, texCoord);
    } else {
        // Si no, usamos el color sólido de antes
        FragColor = vec4(floorColor, 1.0);
    }
}