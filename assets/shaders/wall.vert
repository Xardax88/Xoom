#version 460 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoordIn;
out vec2 texCoord;
uniform mat4 modelview;
uniform mat4 projection;
void main() {
    gl_Position = projection * modelview * vec4(position, 1.0);
    texCoord = texCoordIn;
}