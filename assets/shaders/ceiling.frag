#version 460 core

// La salida del shader: el color final del fragmento (píxel)
out vec4 FragColor;

// Entrada desde el vertex shader
in vec2 texCoord;
// Recibe la posición mundial del fragmento
in vec3 fragWorldPos;

// Uniforms desde Python
uniform sampler2D floorTexture;
uniform vec3 floorColor = vec3(0.5, 0.5, 0.5);
uniform bool useTexture;

// Uniforms para iluminación dinámica
uniform vec3 lightPosition;      // Posición de la luz puntual
uniform vec3 lightColor;         // Color de la luz puntual
uniform float lightIntensity;    // Intensidad de la luz puntual
uniform float lightRange;        // Rango máximo de la luz puntual
uniform vec3 globalLightColor;   // Color de la luz global
uniform float globalLightIntensity; // Intensidad de la luz global

// Modelo de iluminación: luz puntual + luz global
void main()
{
    vec4 baseColor = useTexture ? texture(floorTexture, texCoord) : vec4(floorColor, 1.0);

    float dist = length(lightPosition - fragWorldPos);

    float attenuation = 0.0;
    if (dist < lightRange) {
        attenuation = 1.0 / (1.0 + 0.05 * dist + 0.01 * dist * dist);
        attenuation *= 1.0 - (dist / lightRange);
    }

    vec3 point = lightColor * lightIntensity * attenuation;
    vec3 global = globalLightColor * globalLightIntensity;
    vec3 lighting = min(point + global, vec3(1.0));

    FragColor = vec4(baseColor.rgb * lighting, baseColor.a);
}