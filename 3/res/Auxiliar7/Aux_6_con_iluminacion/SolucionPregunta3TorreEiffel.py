# coding=utf-8
"""
Se agrega la torre Eiffel al medio, para mostrarles cómo funcionan
las mallas y que podemos tenerlas almacenadas en objetos
.OBJ
Estos se pueden generar en programas como Blender, Maya, Rhino o
SketchUp. También es común descargarlos de páginas como:
https://3dwarehouse.sketchup.com/search/?q=eiffel%20tower
https://quixel.com/megascans/home?category=3D%20asset&category=building
Etc. Lo ideal es googlear por .OBJ o .OFF 3D models
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg
import grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath
import off_obj_reader as obj

import modelo


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
###########################################################
        self.theta = np.pi
        self.eye = [0, 0, 0.1]
        self.at = [0, 1, 0.1]
        self.up = [0, 0, 1]
###########################################################


# global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS and action != glfw.REPEAT:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    
###########################################################

    elif key == glfw.KEY_W:
        controller.eye += (controller.at - controller.eye) * 0.05
        controller.at += (controller.at - controller.eye) * 0.05


###########################################################
    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Dice", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs for textures and for colors
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    lightShaderProgram = ls.SimpleGouraudShaderProgram()  # Spoiler de luces
    textureLightShaderProgram = ls.SimpleTextureGouraudShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory

    skybox = modelo.create_skybox(textureLightShaderProgram)
    floor = modelo.create_floor(textureShaderProgram)

    # Creamos una GPUShape a partir de un obj
    # Acá pueden poner carrot.obj, eiffel.obj, suzanne.obj
    shapeSuzanne = obj.readOBJ(getAssetPath('eiffel.obj'), (1.0, 0.0, 0.0))
    gpuSuzanne = es.GPUShape().initBuffers()
    lightShaderProgram.setupVAO(gpuSuzanne)
    gpuSuzanne.fillBuffers(shapeSuzanne.vertices, shapeSuzanne.indices, GL_STATIC_DRAW)

    # View and projection
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)

    t0 = glfw.get_time()
    camera_theta = -3 * np.pi / 4

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    t1 = glfw.get_time()
    t1 = glfw.get_time()

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            controller.theta += 2 * dt

        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            controller.theta -= 2 * dt

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            controller.eye += (controller.at - controller.eye) * dt
            controller.at += (controller.at - controller.eye) * dt

        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            controller.eye -= (controller.at - controller.eye) * dt
            controller.at -= (controller.at - controller.eye) * dt

        at_x = controller.eye[0] + np.cos(controller.theta)
        at_y = controller.eye[1] + np.sin(controller.theta)
        controller.at = np.array([at_x, at_y, controller.at[2]])

        view = tr.lookAt(controller.eye, controller.at, controller.up)

###########################################################################

        # Drawing dice (with texture, another shader program)
        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)

        sg.drawSceneGraphNode(floor, textureShaderProgram, "model")
        
        # Dibujamos el modelo de Suzanne con OBJ:
        # Indicamos que usamos el modelo de luz
        # Se escala, se rota y se sube, en ese orden
        suzanne_transform = tr.matmul(
            [
                # tr.translate(0.0, 0.0, 0.3),
                tr.rotationX(np.pi/2),
                tr.uniformScale(0.00003),
            ]
        )

        glUseProgram(lightShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "model"), 1, GL_TRUE, suzanne_transform)
        glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        # Esto es para indicarle al shader de luz parámetros, pero por ahora no lo veremos
        lightShaderProgram.set_light_attributes() # IGNORAR
        lightShaderProgram.drawCall(gpuSuzanne)


        glUseProgram(textureLightShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureLightShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureLightShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        textureLightShaderProgram.set_light_attributes()
        sg.drawSceneGraphNode(skybox, textureLightShaderProgram, "model")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
