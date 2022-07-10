import glfw
from lib.grafica import basic_shapes as bs
from lib.grafica import easy_shaders as es
from lib.grafica import transformations as tr
from lib.grafica import scene_graph as sg
from lib.grafica import lighting_shaders as ls
from lib import catrom
from OpenGL.GL import *
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Controller():
    def __init__(self):
        self.rotation = False
        self.view = 2
        self.fillPolygon = True
        self.viewSpline = True
        self.viewAxis = True


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
        controller.viewSpline = not controller.viewSpline

    elif key == glfw.KEY_A:
        controller.viewAxis = not controller.viewAxis

    elif key == glfw.KEY_Q:
        glfw.set_window_should_close(window, True)

    else:
        print("Unknown key")


def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape


def createColorPyramid(color):
    sq = np.sqrt(2)
    vertices = [
        -0.5,  0.0,  0.0,           *color, 0, 1, 0,
         0.5,  0.0,  0.0,           *color, 0, 1, 0,
         0.0,  0.0,  np.sqrt(0.75), *color, 0, 1, 0,

        -0.5, -1.0,  0.0,           *color, 0, 0, 1,
         0.5, -1.0,  0.0,           *color, 0, 0, 1,
         0.5,  0.0,  0.0,           *color, 0, 0, 1,
        -0.5,  0.0,  0.0,           *color, 0, 0, 1,

         0.5,  0.0,  0.0,           *color, np.cos(30), 0, np.sin(30),
         0.5, -1.0,  0.0,           *color, np.cos(30), 0, np.sin(30),
         0.0,  0.0,  np.sqrt(0.75), *color, np.cos(30), 0, np.sin(30),

         0.5, -1.0,  0.0,           *color, 0, -sq * np.sin(32), sq * np.cos(32),
        -0.5, -1.0,  0.0,           *color, 0, -sq * np.sin(32), sq * np.cos(32),
         0.0,  0.0,  np.sqrt(0.75), *color, 0, -sq * np.sin(32), sq * np.cos(32),

        -0.5, -1.0,  0.0,           *color, -np.cos(30), 0, np.sin(30),
        -0.5,  0.0,  0.0,           *color, -np.cos(30), 0, np.sin(30),
         0.0,  0.0,  np.sqrt(0.75), *color, -np.cos(30), 0, np.sin(30),
    ]

    indices = [
        0, 1, 2,
        3, 4, 5,
        5, 6, 3,
        7, 8, 9,
        10, 11, 12,
        13, 14, 15
    ]

    return bs.Shape(vertices, indices)


def createBlueQuad():
    color1 = [135 / 255, 206 / 255, 235 / 255]
    color2 = [0,       191/255, 1      ]
    vertices = [
        -1.0,  0.0, -1.0, *color1, 0, 1, 0,
         1.0,  0.0, -1.0, *color1, 0, 1, 0,
         1.0,  0.0,  1.0, *color2, 0, 1, 0,
        -1.0,  0.0,  1.0, *color2, 0, 1, 0
    ]

    indices = [
        0, 1, 2, 2, 3, 0
    ]

    return bs.Shape(vertices, indices)


# res es de hecho el número de paralelepípedos con los que se 
# crea el cilindro (de resolución)
def createMast(pipeline, res):
    color = [42 / 255, 25 / 255, 17 / 255]
    rate = 180 / res
    mastil = sg.SceneGraphNode("mastil")
    for i in range(res):
        name = "quad" + str(i)
        brownCube = bs.createColorNormalsCube(*color)
        gpuBrownCube = createGPUShape(pipeline, brownCube)
        brownCubeNode = sg.SceneGraphNode(name)
        brownCubeNode.transform = tr.matmul([
            tr.rotationY(rate * i)
        ])
        brownCubeNode.childs += [gpuBrownCube]
        mastil.childs += [brownCubeNode]
    return mastil


def createBoat(pipeline):
    brown = [139 / 255, 69 / 255, 19 / 255]
    skyBlue = [92 / 255, 208 / 255, 249 / 255]
    pink = [248 / 255, 168 / 255, 181 / 255]

    # Figuras en memoria
    brownCube = bs.createColorNormalsCube(*brown)
    gpuBrownCube = createGPUShape(pipeline, brownCube)

    brownPyramid = createColorPyramid(brown)
    gpuBrownPyramid = createGPUShape(pipeline, brownPyramid)

    skyBlueCube = bs.createColorNormalsCube(*skyBlue)
    gpuSkyBlueCube1 = createGPUShape(pipeline, skyBlueCube)
    gpuSkyBlueCube2 = createGPUShape(pipeline, skyBlueCube)

    pinkCube = bs.createColorNormalsCube(*pink)
    gpuPinkCube1 = createGPUShape(pipeline, pinkCube)
    gpuPinkCube2 = createGPUShape(pipeline, pinkCube)

    whiteCube = bs.createColorNormalsCube(1, 1, 1)
    gpuWhiteCube = createGPUShape(pipeline, whiteCube)

    # Cuerpo del barco
    cuerpo = sg.SceneGraphNode("cuerpo")
    cuerpo.transform = tr.scale(2, 1, 1)
    cuerpo.childs += [gpuBrownCube]

    # Proa y popa
    proa = sg.SceneGraphNode("proa")
    proa.transform = tr.matmul([
        tr.translate(1, 0.5, 0),
        tr.rotationY(np.pi / 2)
    ])
    proa.childs += [gpuBrownPyramid]

    popa = sg.SceneGraphNode("popa")
    popa.transform = tr.matmul([
        tr.translate(-1, 0.5, 0),
        tr.rotationY(-np.pi / 2)
    ])
    popa.childs += [gpuBrownPyramid]

    # Mástil
    mastil = createMast(pipeline, 100)
    mastil.transform = tr.matmul([
        tr.translate(0, 1, 0),
        tr.scale(0.1, 1.8, 0.1)
    ])

    # Bandera
    # Desde arriba hacia abajo
    scaleMatrix = tr.scale(2, 0.2, 0.1)
    skyBlueStripe1 = sg.SceneGraphNode("skyBlueStripe1")
    skyBlueStripe1.transform = tr.matmul([
        scaleMatrix
    ])
    skyBlueStripe1.childs += [gpuSkyBlueCube1]

    pinkStripe1 = sg.SceneGraphNode("pinkStripe1")
    pinkStripe1.transform = tr.matmul([
        tr.translate(0, -0.2, 0),
        scaleMatrix
    ])
    pinkStripe1.childs += [gpuPinkCube1]

    whiteStripe = sg.SceneGraphNode("whiteStripe")
    whiteStripe.transform = tr.matmul([
        tr.translate(0, -0.4, 0),
        scaleMatrix
    ])
    whiteStripe.childs += [gpuWhiteCube]

    pinkStripe2 = sg.SceneGraphNode("pinkStripe2")
    pinkStripe2.transform = tr.matmul([
        tr.translate(0, -0.6, 0),
        scaleMatrix
    ])
    pinkStripe2.childs += [gpuPinkCube2]
    
    skyBlueStripe2 = sg.SceneGraphNode("skyBlueStripe2")
    skyBlueStripe2.transform = tr.matmul([
        tr.translate(0, -0.8, 0),
        scaleMatrix
    ])
    skyBlueStripe2.childs += [gpuSkyBlueCube2]

    bandera = sg.SceneGraphNode("bandera")
    bandera.transform = tr.matmul([
        tr.translate(0, 2, 0),
        tr.uniformScale(0.8)
    ])
    bandera.childs += [skyBlueStripe1, pinkStripe1, whiteStripe, pinkStripe2, skyBlueStripe2]

    # Uniendo todo
    barco = sg.SceneGraphNode("barco")
    barco.transform = tr.uniformScale(0.04)
    barco.childs += [cuerpo, proa, popa, mastil, bandera]

    barcoVista = sg.SceneGraphNode("barcoVista")
    barcoVista.childs += [barco]

    return barcoVista


def createEnvironment(pipeline):
    # Figuras a memoria
    blueQuad = createBlueQuad()
    gpuBlueQuad = createGPUShape(pipeline, blueQuad)

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

    width = 1366
    height = 768
    title = ""
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Conectamos on_key a la ventana
    glfw.set_key_callback(window, on_key)

    # Elegimos dos shaders, uno simple para la spline y uno de luces para los objetos
    simplePipeline = es.SimpleModelViewProjectionShaderProgram()
    lightingPipeline = ls.SimplePhongShaderProgram()

    # Color del background
    glClearColor(0.6, 0.6, 0.6, 1.0)

    # Como trabajamos en 3D activamos la detección de profundidad
    glEnable(GL_DEPTH_TEST)

    # Creamos el grafo de escena
    sceneNode = createScene(lightingPipeline)

    # Seteamos proyección
    projection = tr.perspective(30, float(width) / float(height), 0.1, 100)

    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    simplePipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    # Leemos vértices y generamos la spline
    with open(sys.argv[1], "r") as f:
        lines = f.read().splitlines()

    vertices = []

    for line in lines:
        line = line.replace(",", "")
        vert = [float(x) for x in line.split()]
        vertices += [vert]

    # 130 fps
    trayectoria = catrom.getSplineFixed(vertices, 130)

    numVertices = len(trayectoria)
    index = 0
    x0, y0 = trayectoria[0][0], trayectoria[0][1]

    traslatedBoatNode = sg.findNode(sceneNode, "barcoTras")
    traslatedBoatNode.transform = tr.translate(x0, 0, y0)

    # Dibujo de la spline en rojo
    spline = bs.Shape([x0, 0, y0, 1, 0, 0], [])
    indices = [1, 2]
    for coord in trayectoria:
        spline.vertices += [coord[0], 0, coord[1], 1, 0, 0]
        spline.indices += indices
        indices[0] += 1
        indices[1] += 1
    # Por alguna razón el último punto de la trayectoria es el (0, 0)
    spline.indices.pop(-1)
    spline.indices.pop(-1)

    gpuSpline = createGPUShape(simplePipeline, spline)

    while not glfw.window_should_close(window):

        # Esperamos botones
        glfw.poll_events()

        # Limpiamos buffers de color y profunidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Movimiento del barco a lo largo de la spline
        x, y = trayectoria[index][0], trayectoria[index][1]
        boatTrayectoryNode = sg.findNode(sceneNode, "barcoTras")
        boatTrayectoryNode.transform = tr.translate(x, 0, y)

        # Modificar hacia dónde mira el barco
        x1, y1 = x - x0, y - y0
        theta = np.arctan2(x1, y1) + np.pi / 2
        boatFacingNode = sg.findNode(sceneNode, "barcoVista")
        boatFacingNode.transform = tr.rotationY(theta)
        x0, y0 = x, y

        # 4 distintas cámaras
        match controller.view:
            case 1:
                view = tr.lookAt(
                    np.array([x, 0.05, y]),
                    np.array([x + x1, 0.05, y + y1]),
                    np.array([0, 1, 0])
                )
                viewPos = np.array([x, 0.05, y])

            case 2:
                view = tr.lookAt(
                    np.array([-1, 1, -2]),
                    np.array([0, 0, 0]),
                    np.array([0, 1, 0])
                )
                viewPos = np.array([-1, 1, -2])
            #case 3:

            #case 4:

        glUseProgram(simplePipeline.shaderProgram)

        glUniformMatrix4fv(glGetUniformLocation(simplePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        glUniformMatrix4fv(glGetUniformLocation(simplePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(simplePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        if controller.viewAxis:
            simplePipeline.drawCall(gpuAxis, GL_LINES)
        if controller.viewSpline:
            simplePipeline.drawCall(gpuSpline, GL_LINES)

        glUseProgram(lightingPipeline.shaderProgram)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        # Lighting parameters

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.2, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), -5, 5, 5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                    viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 50)

        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        # Dibujamos la escena
        sg.drawSceneGraphNode(sceneNode, lightingPipeline, "model")

        glfw.swap_buffers(window)

        # Esto solo hace que el movimiento del barco esté en loop
        if index == numVertices - 1:
            index = 0
        else:
            index += 1

    # Limpiamos memoria de la GPU
    sceneNode.clear()

    glfw.terminate()
