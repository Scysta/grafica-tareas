import glfw
import numpy as np
import random
import sys
from OpenGL.GL import *
from grafica.gpu_shape import GPUShape
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.text_renderer as tx


# Clase simple para guardar variables de control en
# la aplicación
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.fly = False
        self.monkey_pos = 0
        self.points = 0
        self.gameOver = False


controller = Controller()


# Función para procesar el input de la aplicación
def on_key(window, key, scancode, action, mods):

    global controller

    if not controller.gameOver:
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

    else:
        if key == glfw.KEY_Q:
            glfw.set_window_should_close(window, True)

        elif key == glfw.KEY_R:
            pass

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
            self.height = banana.height + 1
        else:
            self.height = banana.height - 1

    def textureSetup(self):
        self.gpuShape.texture = es.textureSimpleSetup(self.texture,
            GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    def draw(self, paused):
        dPillar = 0.005 * 0.7
        if paused:
            dPillar = 0
        self.position -= dPillar

        if self.reversed:
            M = tr.matmul([
                tr.translate(self.position, self.height, 0),
                tr.scale(0.25, 1.6, 0),
                tr.rotationZ(np.pi)
            ])

        else:
            M = tr.matmul([
                tr.translate(self.position, self.height, 0),
                tr.scale(0.25, 1.6, 0)
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
        self.position += 2.4

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

    def draw(self, paused):
        dBanana = 0.005 * 0.7
        if paused:
            dBanana = 0
        self.position -= dBanana
        M = tr.matmul([
            tr.translate(self.position, self.height, 0),
            tr.scale(0.12, 0.13, 1)
        ])
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 1, GL_TRUE, M)
        self.pipeline.drawCall(self.gpuShape)


def bananaCheck(monkey_pos, banana):
    diff = (-0.5 - banana.position, monkey_pos - banana.height)
    dist = np.linalg.norm(diff)
    return dist < 0.14


def collisionCheck(monkey_pos, pilar):
    groundCheck = monkey_pos <= -0.8
    pillarCheck1 = pilar.position + 0.11 >= -0.5 and pilar.position - 0.11 <= -0.5
    pillarCheck2 = monkey_pos >= pilar.height + 1.2 or monkey_pos <= pilar.height + 0.8
    return groundCheck or (pillarCheck1 and pillarCheck2)


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
    textPipeline = tx.TextureTextRendererShaderProgram()

    background = bs.createTextureQuad(width / 1000, height / 1000)
    gpuBackground1 = createGpuShape(pipeline, background)
    gpuBackground1.texture = es.textureSimpleSetup("assets/jungle1.png",
        GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    gpuBackground2 = createGpuShape(pipeline, background)
    gpuBackground2.texture = es.textureSimpleSetup("assets/jungle2.png",
        GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

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

    # Set banana and pillars position
    bananaSet = []
    bananaQueue = []
    pilarSet = []
    for i in [0, 1, 2, 3]:
        banana = Banana(pipeline)
        banana.position += i * 0.6
        banana.randomHeight()
        banana.textureSetup()
        bananaSet.append(banana)

        pilar = Pillar(pipeline)
        reversedPilar = Pillar(pipeline, reversed=True)

        pilar.reset(banana)
        reversedPilar.reset(banana)

        pilar.textureSetup()
        reversedPilar.textureSetup()

        pilarSet.append((pilar, reversedPilar))

    textBitsTexture = tx.generateTextBitsTexture()
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)

    pointCounterText = str(controller.points)
    pointCounterShape = tx.textToShape(pointCounterText, 0.1, 0.1)
    gpuPointCounter = createGpuShape(textPipeline, pointCounterShape)
    gpuPointCounter.texture = gpuText3DTexture
    pointCounterTransform = tr.matmul([
        tr.translate(0, 0.8, 0)
    ])

    gameOverText = "Game Over"
    gameOverCharSize = 0.2
    gameOverShape = tx.textToShape(gameOverText, gameOverCharSize - 0.08, gameOverCharSize)
    gpuGameOver = createGpuShape(textPipeline, gameOverShape)
    gpuGameOver.texture = gpuText3DTexture
    gameOverTransform = tr.matmul([
        tr.translate(-(gameOverCharSize - 0.08) * len(gameOverText) / 2, 0.1, -0)
    ])

    retryText = "Press R to retry"
    retryCharSize = 0.1
    retryShape = tx.textToShape(retryText, retryCharSize - 0.01, retryCharSize)
    gpuRetry = createGpuShape(textPipeline, retryShape)
    gpuRetry.texture = gpuText3DTexture
    retryTransform = tr.matmul([
        tr.translate(-(retryCharSize - 0.01) * len(retryText) / 2, -0.1, 0)
    ])

    quitText = "or Q to quit"
    quitCharSize = 0.1
    quitShape = tx.textToShape(quitText, quitCharSize - 0.01, quitCharSize)
    gpuQuit = createGpuShape(textPipeline, quitShape)
    gpuQuit.texture = gpuText3DTexture
    quitTransform = tr.matmul([
        tr.translate(-(quitCharSize - 0.01) * len(quitText) / 2, -0.2, 0)
    ])

    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Activamos transparencias
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    if len(sys.argv) > 1:
        pointGoal = int(sys.argv[1])
    else:
        pointGoal = -1

    dBackground1 = 0
    dBackground2 = -2
    dGround = 0

    while not glfw.window_should_close(window):

        # Le decimos a glfw que espere inputs
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)

        if controller.fillPolygon:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


        glUseProgram(pipeline.shaderProgram)

        backgroundTransform1 = tr.matmul([
            tr.translate(-dBackground1, 0, 0),
            tr.uniformScale(2)
        ])
        backgroundTransform2 = tr.matmul([
            tr.translate(-dBackground2, 0, 0),
            tr.uniformScale(2)
        ])

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, backgroundTransform1)
        pipeline.drawCall(gpuBackground1)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, backgroundTransform2)
        pipeline.drawCall(gpuBackground2)

        # Make the monkey fly and make it so it they can't go above the window
        if controller.fly:
            if controller.monkey_pos >= 0.94:
                controller.monkey_pos += 0.008
            else:
                controller.monkey_pos += 0.016

        # Banana positions
        for banana in bananaSet:
            if bananaCheck(controller.monkey_pos, banana):
                banana.bananaGet()
                bananaSet.pop(0)
                bananaSet.append(banana)
                bananaQueue.append(banana)
            banana.draw(controller.gameOver)

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

        # Setup pilar positions, this could be along banana positions
        for pilar in pilarSet:
            if pilar[0].position <= -1.2:
                pilar[0].reset(bananaQueue[0])
                pilar[1].reset(bananaQueue[0])
                bananaQueue.pop(0)
            if collisionCheck(controller.monkey_pos, pilar[0]):
                controller.gameOver = True
            pilar[0].draw(controller.gameOver)
            pilar[1].draw(controller.gameOver)

        groundTransform1 = tr.matmul([
            tr.translate(0 - dGround, -0.9, 0),
            tr.scale(2, 0.2, 1)
        ])

        groundTransform2 = tr.matmul([
            tr.translate(2 - dGround, -0.9, 0),
            tr.scale(2, 0.2, 1)
        ])

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, groundTransform1)
        pipeline.drawCall(gpuGround1)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, groundTransform2)
        pipeline.drawCall(gpuGround2)

        # Win condition
        if controller.points == pointGoal:
            controller.gameOver = True

        # While you don't crash
        if not controller.gameOver:
            if dBackground1 >= 2:
                dBackground1 -= 3.99
            else:
                dBackground1 += 0.005

            if dBackground2 >= 2:
                dBackground2 -= 3.99
            else:
                dBackground2 += 0.005

            if dGround >= 2:
                dGround = 0
            else:
                dGround += 0.005 * 0.7

            # DELETE
            controller.monkey_pos -= 0.008
        else:
            # Game Over
            controller.fly = False

            # If you reach the needed points
            if controller.points == pointGoal:
                gameOverText = "You Won!"
                gameOverShape = tx.textToShape(gameOverText, gameOverCharSize - 0.08, gameOverCharSize)
                gpuGameOver.fillBuffers(gameOverShape.vertices, gameOverShape.indices, GL_STREAM_DRAW)
                gameOverTransform = tr.matmul([
                    tr.translate(-(gameOverCharSize - 0.08) * len(gameOverText) / 2, 0.1, -0)
                ])

            glUseProgram(textPipeline.shaderProgram)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1, 1, 1, 1)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0, 0, 0, 0)
            glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, pointCounterTransform)
            textPipeline.drawCall(gpuPointCounter)

            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0, 0, 0, 0.5)
            glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, gameOverTransform)
            textPipeline.drawCall(gpuGameOver)

            glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, retryTransform)
            textPipeline.drawCall(gpuRetry)

            glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, quitTransform)
            textPipeline.drawCall(gpuQuit)

            # Retry game
            if glfw.get_key(window, glfw.KEY_R) == glfw.PRESS:
                # Reset monkey position
                controller.monkey_pos = 0

                # Reset point counter
                controller.points = 0

                # Reset banana and pillar position
                for i in [0, 1, 2, 3]:
                    banana = bananaSet[i]
                    banana.position = i * 0.6
                    banana.randomHeight()

                    pilar = pilarSet[i][0]
                    reversedPilar = pilarSet[i][1]

                    pilar.reset(banana)
                    reversedPilar.reset(banana)

                bananaQueue.clear()

                controller.gameOver = False

                if gameOverText != "Game Over":
                    gameOverText = "Game Over"
                    gameOverShape = tx.textToShape(gameOverText, gameOverCharSize - 0.08, gameOverCharSize)
                    gpuGameOver.fillBuffers(gameOverShape.vertices, gameOverShape.indices, GL_STREAM_DRAW)
                    gameOverTransform = tr.matmul([
                        tr.translate(-(gameOverCharSize - 0.08) * len(gameOverText) / 2, 0.1, -0)
                    ])

        # Text setup
        glUseProgram(textPipeline.shaderProgram)
        pointCounterText = str(controller.points)
        pointCounterShape = tx.textToShape(pointCounterText, 0.1, 0.1)
        gpuPointCounter.fillBuffers(pointCounterShape.vertices, pointCounterShape.indices, GL_STREAM_DRAW)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1, 1, 1, 1)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0, 0, 0, 0)
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, pointCounterTransform)
        textPipeline.drawCall(gpuPointCounter)

        glfw.swap_buffers(window)

    gpuMonkey.clear()
    gpuBackground1.clear()
    gpuBackground2.clear()
    for banana in bananaSet:
        banana.gpuShape.clear()
    for pilar in pilarSet:
        pilar[0].gpuShape.clear()
        pilar[1].gpuShape.clear()

    glfw.terminate()
