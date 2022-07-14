import glfw
from OpenGL.GL import *
from grafica.gpu_shape import GPUShape
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr


# Clase simple para guardar variables de control en
# la aplicación
class Controller:
    def __init__(self):
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
    def __init__(self, pipeline, position=0):
        shape = bs.createTextureQuad(1, 1)
        self.pipeline = pipeline
        self.position = position
        self.hitbox = ''
        self.gpuShape = createGpuShape(self.pipeline, shape)

    def reset(self):
        self.position = 2

    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([]))
        self.pipeline.drawCall(self.gpuShape)


class Banana:
    def __init__(self, pipeline, position=0):
        shape = bs.createTextureQuad(1, 1)
        self.pipeline = pipeline
        self.position = position
        self.gpuShape = createGpuShape(self.pipeline, shape)
        self.texture = "assets/banana.png"

    def reset(self):
        self.position = 2

    def bananaGet(self):
        self.reset()
        controller.points += 1

    def textureSetup(self):
        self.gpuShape.texture = es.textureSimpleSetup(self.texture,
            GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    def draw(self):
        M = tr.matmul([
            tr.translate(self.position, 0, 0),
            tr.scale(0.09, 0.1, 1)
        ])
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 1, GL_TRUE, M)
        self.pipeline.drawCall(self.gpuShape)


# Main loop
if __name__ == "__main__":

    # Inicializamos glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Creamos la ventana
    width = 1366
    height = 768

    window = glfw.create_window(width, height, "Flappy bird!", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Conectamos keybinds a la ventana
    glfw.set_key_callback(window, on_key)

    # Shaders
    pipeline = es.SimpleTextureTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    background1 = bs.createTextureQuad(1000 / width, 1000 / height)
    gpuBackground1 = createGpuShape(pipeline, background1)
    gpuBackground1.texture = es.textureSimpleSetup("assets/background.png",
        GL_REPEAT, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    background2 = bs.createTextureQuad(1000 / width, 1000 / height)
    gpuBackground2 = createGpuShape(pipeline, background2)
    gpuBackground2.texture = es.textureSimpleSetup("assets/background.png",
        GL_REPEAT, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    cloud = bs.createTextureQuad(1, 1)
    gpuCloud = createGpuShape(pipeline, cloud)
    gpuCloud.texture = es.textureSimpleSetup("assets/cloud.png",
        GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    monkey = bs.createTextureQuad(1, 1)
    gpuMonkey = createGpuShape(pipeline, monkey)
    gpuMonkey.texture = es.textureSimpleSetup("assets/monkey.png",
        GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    bananaSet = []
    test = 0
    for i in [0, 1, 2]:
        banana = Banana(pipeline, test)
        banana.textureSetup()
        bananaSet.append(banana)
        test += 0.2

    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Activamos transparencias
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    dx = 0
    dy = 0

    while not glfw.window_should_close(window):

        # Le decimos a glfw que espere inputs
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)

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

        monkeyTransform = tr.matmul([
            tr.translate(-0.5, controller.monkey_pos, 0),
            tr.uniformScale(0.2)
        ])

        cloudTransform = tr.matmul([
            tr.translate(-0.5, controller.monkey_pos - 0.1, 0),
            tr.scale(0.2, 0.15, 1)
        ])

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, monkeyTransform)
        pipeline.drawCall(gpuMonkey)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, cloudTransform)
        pipeline.drawCall(gpuCloud)

        test = 0
        for banana in bananaSet:
            banana.draw()

        if dx >= 2:
            dx = 0
        else:
            dx += 0.005

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
