# Comencé muy tarde la tarea y entre el estudio y cosas esto es lo que alcancé a hacer u.u
# Quería hacer una matriz en numpy con cada celda de la grilla, pero me di cuenta tarde de
# que no podía interpretarse así tan fácilmente, quizá solo debí guardar el color 
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from grafica import basic_shapes as bs
from grafica import easy_shaders as es
from grafica import gpu_shape
from grafica import transformations

class Controller:
    activeColor = None

controller = Controller()

# GLFW key recognition
def on_key(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return

    global controller

    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


# Main loop as function
def pixelPaint(size):
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Creamos la ventana dependiendo del número de grillas
    width = size*10
    height = (size + 2) * 10

    window = glfw.create_window(width, height, "Pixel Paint", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    glfw.set_key_callback(window, on_key)

    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    glClearColor(239/255, 239/255, 239/255, 1.0)

    trans = [190/255, 190/255, 190/255]

    vertexData = [
            -0.5, -0.5, 0.0, *trans,
             0.5, -0.5, 0.0, *trans,
             0.5,  0.5, 0.0, *trans,
            -0.5,  0.5, 0.0, *trans
            ]

    indices = [0, 1, 2, 0, 2, 3]
    
    grid = np.zeros((size, size), dtype=gpu_shape.GPUShape())

    for i in range(size):
        for j in range(size):
            gpuCell = gpu_shape.GPUShape()
            gpuCell.initBuffers()
            pipeline.setupVAO(gpuCell)
            gpuCell.fillBuffers(vertexData, indices, GL_STATIC_DRAW)
            grid[i][j] = gpuCell

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    (x, y) = (0.1, 0.1)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)
        
        # Esto debería crear size x size cuadrados escalados y trasladados
        # para colocarlos en una grilla (matriz)
        for i in range(size):
            for j in range(size):
                glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
                    tr.translate(-0.965 + j*x, 0.965 + i*y, 0),
                    tr.scale(1/10, 1/10, 0)]))
                pipeline.drawCall(grid[i][j])


    for i in range(size):
        for j in range(size):
            grid[i][j].clear()
    glfw.terminate()

