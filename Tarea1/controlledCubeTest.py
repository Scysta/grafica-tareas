import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica import basic_shapes as bs
from grafica import easy_shaders as es
from grafica import gpu_shape 
from grafica import transformations as tr

class Controller:
    fillPolygon = True
    aIsPressed = False
    rightIsPressed = False
    wIsPressed = False
    downIsPressed = False

controller = Controller()

# GLFW key recognition
# Aquí se colocan todas las teclas que se usan
def on_key(window, key, scancode, action, mods):

    global controller

    if action == glfw.PRESS:

        if key == glfw.KEY_SPACE:
            controller.fillPolygon = not controller.fillPolygon

        elif key == glfw.KEY_W:
            controller.

        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

        else:
            print("Unknown key")

#Main loop
if __name__ == "__main__":

    # Inicializamos GLFW
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Creamos la ventana
    width = 600
    height = 600

    window = glfw.create_window(width, height, "Quad personal test", None, None)

    # Si es que no hay ventana se cierra y termina glfw
    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window,True)

    glfw.make_context_current(window)

    # Conectamos los keybinds a la ventana
    glfw.set_key_callback(window, on_key)

    # Escogemos los shaders 
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Color del background
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Activamos la detección de profundidad
    glEnable(GL_DEPTH_TEST)

    # Escogemos los vértices e índices
    vertexData = [
            -0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.5, 0.0, 1.0, 0.0,
            0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
            -0.5, 0.5, 0.5, 0.5, 0.5, 0.5,

            -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
            0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 0.0, 1.0,
            -0.5, 0.5, -0.5, 0.5, 0.5, 0.5
            ]

    indices = [
             0, 1, 2, 2, 3, 0,
             4, 5, 6, 6, 7, 4,
             4, 5, 1, 1, 0, 4,
             6, 7, 3, 3, 2, 6,
             5, 6, 2, 2, 1, 5,
             7, 4, 0, 0, 3, 7]

    # Generamos la figura y generamos vao, evo y ebo
    gpuCube = gpu_shape.GPUShape()

    # Dibujamos el quad
    gpuCube.initBuffers()
    pipeline.setupVAO(gpuCube)
    gpuCube.fillBuffers(vertexData, indices, GL_STATIC_DRAW)

    # Mientras haya ventana
    while not glfw.window_should_close(window):
        # Activamos los keybinds con glfw
        glfw.poll_events()

        # Llenamos la figura dependiendo del controller
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else: 
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Limpiamos la pantalla 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        theta = glfw.get_time()
        Rx = tr.rotationX(np.pi/3)
        Ry = tr.rotationY(theta)
        M = np.matmul(Rx, Ry)

        # Probamos transformaciones
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, M)

        # Dibujamos el quad
        pipeline.drawCall(gpuCube)

        glfw.swap_buffers(window)

    # Limpiamos memoria
    gpuCube.clear()
    glfw.terminate()
