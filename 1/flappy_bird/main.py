import glfw
import numpy as np
import random
from OpenGL.GL import *
from grafica.gpu_shape import GPUShape
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr


# Clase simple para guardar variables de control en
# la aplicación
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.fly = False
        self.monkey_pos = 0
        self.points = 0


controller = Controller()


# Función para procesar el input de la aplicación
def on_key(window, key, scancode, action, mods):

    global controller

    if (action == glfw.PRESS or action == glfw.REPEAT) and key == glfw.KEY_UP:
        controller.fly = True

    elif action == glfw.RELEASE and key == glfw.KEY_UP:
        controller.fly = False

    elif key == glfw.KEY_SPACE and action == glfw.PRESS:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_Q:
        glfw.set_window_should_close(window, True)

    else:
        print("Unknown key")


def createGpuShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape


class Pillar:
    def __init__(self, pipeline, position=0, height=0, reversed=False):
        shape = bs.createTextureQuad(1, 1)
        self.pipeline = pipeline
        self.position = position
        self.height = height
        self.gpuShape = createGpuShape(self.pipeline, shape)
        self.texture = "assets/pipe.png"
        self.reversed = reversed

    def reset(self, banana):
        self.position = banana.position + 0.01
        if self.reversed:
            self.height = banana.height + 0.6
        else:
            self.height = banana.height - 0.6

    def textureSetup(self):
        self.gpuShape.texture = es.textureSimpleSetup(self.texture,
            GL_CLAMP_TO_EDGE, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    def draw(self):
        self.position -= 0.005 * 0.7
        if self.reversed:
            M = tr.matmul([
                tr.translate(self.position, self.height, 0),
                tr.scale(0.2, 0.75, 0),
                tr.rotationZ(np.pi)
            ])

        else:
            M = tr.matmul([
                tr.translate(self.position, self.height, 0),
                tr.scale(0.2, 0.75, 0)
            ])

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, M)
        self.pipeline.drawCall(self.gpuShape)


class Banana:
    def __init__(self, pipeline, position=0, height=0):
        shape = bs.createTextureQuad(1, 1)
        self.pipeline = pipeline
        self.position = position
        self.height = height
        self.gpuShape = createGpuShape(self.pipeline, shape)
        self.texture = "assets/banana.png"

    def reset(self):
        self.position = 1.05

    def textureSetup(self):
        self.gpuShape.texture = es.textureSimpleSetup(self.texture,
            GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    def randomHeight(self):
        r = random.randint(-50, 50) / 70
        self.height = r

    def bananaGet(self):
        self.position += 2.4
        self.randomHeight()
        controller.points += 1

    def draw(self):
        self.position -= 0.005 * 0.7
        M = tr.matmul([
            tr.translate(self.position, self.height, 0),
            tr.scale(0.09, 0.1, 1)
        ])
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 1, GL_TRUE, M)
        self.pipeline.drawCall(self.gpuShape)


def bananaCheck(monkey_pos, banana):
    diff = (-0.5 - banana.position, monkey_pos - banana.height)
    dist = np.linalg.norm(diff)
    return dist < 0.07


# Main loop
if __name__ == "__main__":

    # Inicializamos glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Creamos la ventana
    width = 1366
    height = 768

    window = glfw.create_window(width, height, "Flappy monkey!", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Conectamos keybinds a la ventana
    glfw.set_key_callback(window, on_key)

    # Shaders
    pipeline = es.SimpleTextureTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    background = bs.createTextureQuad(1000 / width, 1000 / height)
    gpuBackground1 = createGpuShape(pipeline, background)
    gpuBackground1.texture = es.textureSimpleSetup("assets/background.png",
        GL_REPEAT, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    gpuBackground2 = createGpuShape(pipeline, background)
    gpuBackground2.texture = es.textureSimpleSetup("assets/background.png",
        GL_REPEAT, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    ground = bs.createTextureQuad(3, 1)
    gpuGround1 = createGpuShape(pipeline, ground)
    gpuGround1.texture = es.textureSimpleSetup("assets/ground.png",
        GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    gpuGround2 = createGpuShape(pipeline, ground)
    gpuGround2.texture = es.textureSimpleSetup("assets/ground.png",
        GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    cloud = bs.createTextureQuad(1, 1)
    gpuCloud = createGpuShape(pipeline, cloud)
    gpuCloud.texture = es.textureSimpleSetup("assets/cloud.png",
        GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    monkey = bs.createTextureQuad(1, 1)
    gpuMonkey = createGpuShape(pipeline, monkey)
    gpuMonkey.texture = es.textureSimpleSetup("assets/monkey.png",
        GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    bananaSet = []
    bananaQueue = []
    for i in [0, 1, 2, 3]:
        banana = Banana(pipeline)
        banana.position += i * 0.6
        banana.randomHeight()
        banana.textureSetup()
        bananaSet.append(banana)

    pilarSet = []
    for i in [0, 1, 2, 3]:
        pilar = Pillar(pipeline)
        reversedPilar = Pillar(pipeline, reversed=True)

        pilar.position = bananaSet[i].position + 0.001
        reversedPilar.position += bananaSet[i].position + 0.001

        pilar.height = bananaSet[i].height - 0.6
        reversedPilar.height = bananaSet[i].height + 0.6

        pilar.textureSetup()
        reversedPilar.textureSetup()

        pilarSet.append((pilar, reversedPilar))

    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Activamos transparencias
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    dx = 0
    dx2 = 0

    while not glfw.window_should_close(window):

        # Le decimos a glfw que espere inputs
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)

        if controller.fillPolygon:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        backgroundTransform1 = tr.matmul([
            tr.translate(-dx, 0, 0),
            tr.uniformScale(2)
        ])
        backgroundTransform2 = tr.matmul([
            tr.translate(-dx + 2, 0, 0),
            tr.uniformScale(2)
        ])

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, backgroundTransform1)
        pipeline.drawCall(gpuBackground1)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, backgroundTransform2)
        pipeline.drawCall(gpuBackground2)

        if controller.fly:
            controller.monkey_pos += 0.016

        for banana in bananaSet:
            if bananaCheck(controller.monkey_pos, banana):
                banana.bananaGet()
                bananaSet.pop(0)
                bananaSet.append(banana)
                bananaQueue.append(banana)
                print(controller.points)
            banana.draw()

        monkeyTransform = tr.matmul([
            tr.translate(-0.5, controller.monkey_pos, 0),
            tr.uniformScale(0.17)
        ])

        cloudTransform = tr.matmul([
            tr.translate(-0.5, controller.monkey_pos - 0.1, 0),
            tr.scale(0.18, 0.13, 1)
        ])

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, monkeyTransform)
        pipeline.drawCall(gpuMonkey)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, cloudTransform)
        pipeline.drawCall(gpuCloud)

        for pilar in pilarSet:
            if pilar[0].position <= -1.2:
                pilar[0].reset(bananaQueue[0])
                pilar[1].reset(bananaQueue[0])
                bananaQueue.pop(0)
            pilar[0].draw()
            pilar[1].draw()

        groundTransform1 = tr.matmul([
            tr.translate(0 - dx2, -0.9, 0),
            tr.scale(2, 0.2, 1)
        ])

        groundTransform2 = tr.matmul([
            tr.translate(2 - dx2, -0.9, 0),
            tr.scale(2, 0.2, 1)
        ])

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, groundTransform1)
        pipeline.drawCall(gpuGround1)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, groundTransform2)
        pipeline.drawCall(gpuGround2)

        if dx >= 2:
            dx = 0
        else:
            dx += 0.005

        if dx2 >= 2:
            dx2 = 0
        else:
            dx2 += 0.005 * 0.7

        if controller.monkey_pos <= -1:
            controller.monkey_pos = 1
        else:
            controller.monkey_pos -= 0.008

        glfw.swap_buffers(window)

    gpuMonkey.clear()
    gpuBackground1.clear()
    gpuBackground2.clear()
    for banana in bananaSet:
        banana.gpuShape.clear()

    glfw.terminate()
