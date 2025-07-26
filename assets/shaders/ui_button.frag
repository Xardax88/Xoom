#version 460 core

// La salida del shader: el color final del fragmento (píxel)
out vec4 FragColor;

// Uniforms para color y textura
uniform vec3 objectColor;
uniform sampler2D textTexture;
uniform int useTexture;
uniform vec2 textOffset;
uniform vec2 textScale;

// Coordenadas de textura interpoladas desde el vértice (calculadas manualmente)
in vec2 TexCoord;

void main() {
    vec2 uv = TexCoord;
    // Ajustar UV para centrar el texto en el botón
    vec2 textUV = (uv - textOffset) / textScale;
    bool inText = all(greaterThanEqual(uv, textOffset)) && all(lessThanEqual(uv, textOffset + textScale));
    if (useTexture == 1 && inText) {
        vec4 textColor = texture(textTexture, textUV);
        // Si el pixel es transparente, muestra el color del botón
        if (textColor.a < 0.1)
            FragColor = vec4(objectColor, 1.0);
        else
            FragColor = textColor;
    } else {
        FragColor = vec4(objectColor, 1.0);
    }
}