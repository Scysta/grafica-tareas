# coding=utf-8
"""
Controlling the movement of a quad.
"""

import grafica.easy_shaders as es
import grafica.basic_shapes as bs
import grafica.transformations as tr
import glfw
from OpenGL.GL import *
import numpy as np
import sys
import os.path
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

__author__ = "Daniel Calderon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    theta = 0.0
    rotate = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return

    global controller

    if key == glfw.KEY_SPACE:
        controller.rotate = not controller.rotate

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(
        width, height, "Mind Controlled Quad", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Creating shapes on GPU memory
    mango = bs.createColorQuad(0, 1, 0)
    gpuMango = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuMango)
    gpuMango.fillBuffers(mango.vertices, mango.indices, GL_STATIC_DRAW)

    cabeza = bs.createColorQuad(1, 0, 0)
    gpuCabeza = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCabeza)
    gpuCabeza.fillBuffers(cabeza.vertices, cabeza.indices, GL_STATIC_DRAW)

    punta = bs.createColorQuad(0, 0, 1)
    gpuPunta = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuPunta)
    gpuPunta.fillBuffers(punta.vertices, punta.indices, GL_STATIC_DRAW)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    t0 = glfw.get_time()

    while not glfw.window_should_close(window):
        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # theta is modified an amount proportional to the time spent in a loop iteration
        if controller.rotate:
            controller.theta += dt

        # Drawing the Quad with the given transformation

        # Punta derecha
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.rotationZ(controller.theta),
            tr.translate(2.5/9, 9/12, 0),
            tr.rotationZ(math.pi/4),
            tr.scale(2*math.sqrt(2)/12, 2*math.sqrt(2)/12, 0)]))
        pipeline.drawCall(gpuPunta)

        # Punta Izquierda
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.rotationZ(controller.theta),
            tr.translate(-2.5/9, 9/12, 0),
            tr.rotationZ(math.pi/4),
            tr.scale(2*math.sqrt(2)/12, 2*math.sqrt(2)/12, 0)]))
        pipeline.drawCall(gpuPunta)

        # Parte Central
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.rotationZ(controller.theta),
            tr.translate(0, 9/12, 0),
            tr.scale(5/9, 4/12, 0)]))
        pipeline.drawCall(gpuCabeza)

        # Mango
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.rotationZ(controller.theta),
            tr.translate(0, 4/12, 0),
            tr.scale(3/9, 6/12, 0)]))
        pipeline.drawCall(gpuMango)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuMango.clear()
    gpuCabeza.clear()
    gpuPunta.clear()

    glfw.terminate()
