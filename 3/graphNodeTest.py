import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica import basic_shapes as bs
from grafica import easy_shaders as es
from grafica import transformations as tr
from grafica import scene_graph as sg
from lib import catrom

class Controller():
    def __init__(self):
        self.rotation = False
        self.view = 2
        self.fillPolygon = True

controller = Controller()

def on_key(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return

    global controller
        
    if key == glfw.KEY_R:
        controller.rotation = not controller.rotation

    elif key == glfw.KEY_1:
        controller.view = 1

    elif key == glfw.KEY_2:
        controller.view = 2

    elif key == glfw.KEY_2:
        controller.view = 3

    elif key == glfw.KEY_3:
        controller.view = 4

    elif key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_Q:
        glfw.set_window_should_close(window, True)

    else: 
        print("Unknown key")

def createColorPyramid(color):
    vertices = [
            -0.5,  0.0,  0.0, *color,
             0.5,  0.0,  0.0, *color,
             0.0,  0.0,  np.sqrt(0.75),  *color,
            -0.5, -1.0,  0.0, *color,
             0.5, -1.0,  0.0, *color
            ]
    indices = [
            0, 1, 2,
            3, 4, 1,
            1, 0, 3,
            4, 2, 1,
            3, 0, 2,
            4, 3, 2
            ]

    return bs.Shape(vertices, indices)

def createBlueQuad():
    color1 = [135/255, 206/255, 235/255]
    color2 = [0,       191/255, 1      ]
    vertices = [
            -1.0,  0.0, -1.0, *color1,
             1.0,  0.0, -1.0, *color1,
             1.0,  0.0,  1.0, *color2,
            -1.0,  0.0,  1.0, *color2
            ]

    indices = [
            0, 1, 2, 2, 3, 0
            ]

    return bs.Shape(vertices, indices)

def createBoat(pipeline):
    color = [139/255, 69/255, 19/255]

    # Figuras en memoria
    brownCube = bs.createColorCube(*color)
    gpuBrownCube = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBrownCube)
    gpuBrownCube.fillBuffers(brownCube.vertices, brownCube.indices, GL_STATIC_DRAW)

    brownPyramid = createColorPyramid(color)
    gpuBrownPyramid = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBrownPyramid)
    gpuBrownPyramid.fillBuffers(brownPyramid.vertices, brownPyramid.indices, GL_STATIC_DRAW)

    #blackCylinder = 
    #gpublackCylinder = es.GPUShape().initBuffers()
    #pipeline.setupVAO(gpublackCylinder)
    #gpublackCylinder.fillBuffers(blackCylinder.vertices, blackCylinder.indices. GL_STATIC_DRAW)

    # Cuerpo del barco
    cuerpo = sg.SceneGraphNode("cuerpo")
    cuerpo.transform = tr.scale(2, 1, 1)
    cuerpo.childs += [gpuBrownCube]

    # Proa y popa
    proa = sg.SceneGraphNode("proa")
    proa.transform = tr.matmul([
        tr.translate(1, 0.5, 0), 
        tr.rotationY(np.pi/2)
        ])
    proa.childs += [gpuBrownPyramid]

    popa = sg.SceneGraphNode("popa")
    popa.transform = tr.matmul([
        tr.translate(-1, 0.5, 0), 
        tr.rotationY(-np.pi/2)
        ])
    popa.childs += [gpuBrownPyramid]

    # Mástil
    #mastil = sg.SceneGraphNode("mastil")
    #mastil.transform = tr.matmul([
    #    tr.translate(0, 1, 0),
    #    tr.scale(0.2, 3, 0.2)
    #    ])
    #mastil.childs += [gpuBrownCylinder]

    ## Bandera
    #bandera = sg.SceneGraphNode("bandera")
    #bandera.transform = tr.matmul([

    #    ])
    #bandera.childs += []

    # Uniendo todo
    barco = sg.SceneGraphNode("barco")
    barco.transform = tr.uniformScale(0.08)
    barco.childs += [cuerpo, proa, popa]

    barcoVista = sg.SceneGraphNode("barcoVista")
    barcoVista.childs += [barco]

    return barcoVista

def createEnvironment(pipeline):
    # Figuras a memoria
    blueQuad = createBlueQuad()
    gpuBlueQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBlueQuad)
    gpuBlueQuad.fillBuffers(blueQuad.vertices, blueQuad.indices, GL_STATIC_DRAW)

    # Mar
    mar = sg.SceneGraphNode("mar")
    mar.childs += [gpuBlueQuad]

    # Isla
    #isla = sg.SceneGraphNode("isla")
    #isla.childs 

    # Ambiente
    ambiente = sg.SceneGraphNode("ambiente")
    ambiente.childs += [mar]

    return ambiente

def createScene(pipeline):
    barcoTras = sg.SceneGraphNode("barcoTras")
    barcoTras.transform = tr.translate(-0.8, 0, 0.8)
    barcoTras.childs += [createBoat(pipeline)]

    escena = sg.SceneGraphNode("escena")
    escena.childs += [createEnvironment(pipeline), barcoTras]

    return escena


if __name__ == "__main__":

    # Inicializamos glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = ""
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

    # Creamos el grafo de escena
    sceneNode = createScene(pipeline)

    # Seteamos proyección 
    projection = tr.perspective(90, float(width) / float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    # Leemos vértices y generamos la spline
    with open(sys.argv[1], "r") as f:
        lines = f.read().splitlines()

    vertices = []

    for line in lines:
        line = line.replace(",", "")
        vert = [float(x) for x in line.split()]
        vertices += [vert]

    # 900 fps 
    trayectoria = catrom.getSplineFixed(vertices, 100)

    numVertices = len(trayectoria)
    index = 0
    x0, y0 = trayectoria[0][0], trayectoria[0][1]

    traslatedBoatNode = sg.findNode(sceneNode, "barcoTras")
    traslatedBoatNode.transform = tr.translate(trayectoria[0][0], 0, trayectoria[0][1])

    while not glfw.window_should_close(window):

        # Esperamos botones
        glfw.poll_events()

        # Limpiamos buffers de color y profunidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        pipeline.drawCall(gpuAxis, GL_LINES)

        # Movimiento del barco a lo largo de la spline
        x, y = trayectoria[index][0], trayectoria[index][1]
        boatTrayectoryNode = sg.findNode(sceneNode, "barcoTras")
        boatTrayectoryNode.transform = tr.translate(x, 0, y)

        # Modificar hacia dónde mira el barco
        x1, y1 = x-x0, y-y0
        theta = np.arctan2(x1, y1) + np.pi/2
        boatFacingNode = sg.findNode(sceneNode, "barcoVista")
        boatFacingNode.transform = tr.rotationY(theta)
        x0, y0 = x, y

        # 4 distintas cámaras 
        match controller.view:
            case 1:
                view = tr.lookAt(
                    np.array([x, 0.1, y]),
                    np.array([x1, 0.1, y1]),
                    np.array([0, 1, 0])
                    )
                glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

            case 2:
                view = tr.lookAt(
                    np.array([-2, 3, -3]),
                    np.array([0, 0, 0]),
                    np.array([0, 1, 0])
                    )
                glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

            #case 3:


            #case 4:

        # Dibujamos la escena
        sg.drawSceneGraphNode(sceneNode, pipeline, "model")

        glfw.swap_buffers(window)

        # Esto solo hace que el movimiento del barco esté en loop
        if index == numVertices - 1:
            index = 0
        else:
            index += 1

    # Limpiamos memoria de la GPU
    sceneNode.clear()

    glfw.terminate()

