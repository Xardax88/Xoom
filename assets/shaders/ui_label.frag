#version 330 core

in vec2 fragTexCoord;

uniform sampler2D textTexture;
uniform int useTexture;

out vec4 FragColor;

void main()
{
    if (useTexture == 1) {
        vec4 texColor = texture(textTexture, fragTexCoord);
        if (texColor.a < 0.05)
            discard;
        FragColor = texColor;
    } else {
        FragColor = vec4(1.0, 1.0, 1.0, 1.0);
    }
}
