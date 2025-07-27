#version 460 core
uniform sampler2D wallTexture;
in vec2 texCoord;
// Recibe la posición mundial del fragmento
in vec3 fragWorldPos;
out vec4 fragColor;

// Uniforms para iluminación dinámica
uniform vec3 lightPosition;   // Posición de la luz puntual
uniform vec3 lightColor;      // Color de la luz puntual
uniform float lightIntensity; // Intensidad de la luz puntual
uniform float lightRange;     // Rango máximo de la luz puntual

uniform vec3 globalLightColor;   // Color de la luz global
uniform float globalLightIntensity; // Intensidad de la luz global

// Modelo de iluminación: luz puntual + luz global
void main() {
    vec4 texColor = texture(wallTexture, texCoord);

    // Calcular distancia real a la luz
    float dist = length(lightPosition - fragWorldPos);

    // Si el fragmento está fuera del rango, la luz puntual no afecta
    float attenuation = 0.0;
    if (dist < lightRange) {
        attenuation = 1.0 / (1.0 + 0.05 * dist + 0.01 * dist * dist);
        // Atenuación adicional suave al acercarse al borde del rango
        attenuation *= 1.0 - (dist / lightRange);
    }

    // Luz puntual: intensidad final
    vec3 point = lightColor * lightIntensity * attenuation;

    // Luz global: constante
    vec3 global = globalLightColor * globalLightIntensity;

    // Color final: suma de ambas luces, limitado a 1.0
    vec3 lighting = min(point + global, vec3(1.0));

    fragColor = vec4(texColor.rgb * lighting, texColor.a);
}