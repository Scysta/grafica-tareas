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
from grafica import scene_graph as sg

class Controller():
    def __init__(self):
        self.rotation = False
        self.view = 2

controller = Controller()

def on_key(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return

    global controller
        
    if key == glfw.KEY_R:
        controller.rotation = not controller.rotation

    elif key == glfw.KEY_Z:
        controller.view = 1

    elif key == glfw.KEY_X:
        controller.view = 2

    elif key == glfw.KEY_Q:
        glfw.set_window_should_close(window, True)

    else: 
        print("Unknown key")

def createPyramid(pipeline):
    # Simplemente creamos las figuras y las mandamos a GPU
    vertices = [
            -0.5, -0.5, -0.5, 1, 0, 0,
             0.5, -0.5, -0.5, 0, 1, 0,
             0.0, -0.5, np.sqrt(0.75), 0, 0, 1,
             0.0, 0.3, (-0.5 + np.sqrt(0.75))/2, 1, 1, 1
            ]
    indices = [
            0, 1, 2,
            1, 2, 3,
            2, 0, 3
          
            ]

    gpuPyramid = gpu_shape.GPUShape()
    gpuPyramid.initBuffers()
    pipeline.setupVAO(gpuPyramid)
    gpuPyramid.fillBuffers(vertices, indices, GL_STATIC_DRAW)
    #redTriangle = bs.createRainbowTriangle()
    #gpuRedTriangle = es.GPUShape().initBuffers()
    #pipeline.setupVAO(gpuRedTriangle)
    #gpuRedTriangle.fillBuffers(redTriangle.vertices, redTriangle.indices, GL_STATIC_DRAW)

    #greenTriangle = bs.createRainbowTriangle()
    #gpuGreenTriangle = es.GPUShape().initBuffers()
    #pipeline.setupVAO(gpuGreenTriangle)
    #gpuGreenTriangle.fillBuffers(greenTriangle.vertices, greenTriangle.indices, GL_STATIC_DRAW)
    #
    #blueTriangle = bs.createRainbowTriangle()
    #gpuBlueTriangle = es.GPUShape().initBuffers()
    #pipeline.setupVAO(gpuBlueTriangle)
    #gpuBlueTriangle.fillBuffers(blueTriangle.vertices, blueTriangle.indices, GL_STATIC_DRAW)

    #grayTriangle = bs.createRainbowTriangle()
    #gpuGrayTriangle = es.GPUShape().initBuffers()
    #pipeline.setupVAO(gpuGrayTriangle)
    #gpuGrayTriangle.fillBuffers(grayTriangle.vertices, grayTriangle.indices, GL_STATIC_DRAW)

    ## Creamos las caras como nodos de grafo
    #bottomFace = sg.SceneGraphNode("bottomFace")
    #bottomFace.transform = tr.matmul([
    #    tr.translate(0, -0.43, 0),
    #    tr.rotationX(np.pi/2)
    #    ])
    #bottomFace.childs += [gpuGrayTriangle]

    #frontFace = sg.SceneGraphNode("frontFace")
    #frontFace.transform = tr.matmul([
    #    tr.translate(0, 0, -0.25),
    #    tr.rotationX(np.pi/6)
    #    ])
    #frontFace.childs += [gpuRedTriangle]

    #rightFace = sg.SceneGraphNode("rightFace")
    #rightFace.transform = tr.matmul([
    #     tr.translate(0.25, 0, 0),
    #     tr.rotationY(np.pi/2.8),
    #     tr.rotationZ(np.pi/2)
    #     ])
    #rightFace.childs += [gpuGreenTriangle]

    #leftFace = sg.SceneGraphNode("leftFace")
    ##leftFace.transform = tr.matmul([
    ##    tr.translate(-0.5, 0, 0),
    ##    tr.rotationY(-np.pi/3),
    ##    tr.rotationZ(-np.pi/3)
    ##    ])
    #leftFace.childs += [gpuBlueTriangle]

    # Conectamos las caras con la pirámide
    pyramid = sg.SceneGraphNode("pyramid")
    pyramid.childs += [gpuPyramid]
    #pyramid.childs += [bottomFace]
    #pyramid.childs += [frontFace]
    #pyramid.childs += [rightFace]
    #pyramid.childs += [leftFace]

    return pyramid

if __name__ == "__main__":

    # Inicializmos glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = "Pyramid with perspective graph test"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Conectamos on_key a la ventana
    glfw.set_key_callback(window, on_key)

    # Elejimos el shader y le decimos a OpenGL que lo use
    pipeline = es.SimpleModelViewProjectionShaderProgram()
    glUseProgram(pipeline.shaderProgram) 

    # Color del background
    glClearColor(0.6, 0.6, 0.6, 1.0)

    # Como trabajamos en 3D activamos la detección de profundidad
    glEnable(GL_DEPTH_TEST)

    # Creamos las figuras en memoria
    pyramidNode = createPyramid(pipeline)

    # Seteamos proyección y vista
    projection = tr.perspective(45, float(width) / float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    theta = 0

    while not glfw.window_should_close(window):

        # Esperamos botones
        glfw.poll_events()

        # Limpiamos buffers de color y profunidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        
        # Hacemos que la pirámide rota constantemente 
        # si la rotación está activada
        if controller.rotation:
            theta += 0.005
            pyramidNode.transform = tr.rotationY(theta)

        if controller.view == 1:
            view = tr.lookAt(
                np.array([5, 5, 10]),
                np.array([0, 0, 0]),
                np.array([0, 0, 1])
                )
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        else:
            view = tr.lookAt(
                np.array([5, 5, 0]),
                np.array([0, 0, 0]),
                np.array([0, 1, 0])
                )
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        pipeline.drawCall(gpuAxis, GL_LINES)

        # Dibujamos la pirámide
        sg.drawSceneGraphNode(pyramidNode, pipeline, "model")

        glfw.swap_buffers(window)

    # Limpiamos memoria de la GPU
    pyramidNode.clear()

    glfw.terminate()

