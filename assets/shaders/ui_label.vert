#version 330 core

// Posición del vértice en pantalla (en píxeles)
layout(location = 0) in vec2 inPosition;

// Uniformes para transformar el quad
uniform mat4 projection;      // Proyección ortográfica de pantalla
uniform vec2 labelPos;        // Posición de la etiqueta (esquina inferior izquierda)
uniform vec2 labelSize;       // Tamaño de la etiqueta (ancho, alto)

// Salida para el fragment shader
out vec2 fragTexCoord;

void main()
{
    // Convertir el quad [0,1]x[0,1] a píxeles de pantalla
    vec2 pos = labelPos + inPosition * labelSize;
    gl_Position = projection * vec4(pos.xy, 0.0, 1.0);

    // Las coordenadas de textura corresponden directamente al quad
    fragTexCoord = inPosition;
}
