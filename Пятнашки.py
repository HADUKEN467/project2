import pygame
import sys
import random
from pygame.locals import *  # доп. константы

BOARDWIDTH = 4
BOARDHEIGHT = 4
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
PURPLE = (255, 192, 203)

BGCOLOR = DARKTURQUOISE
TILECOLOR = PURPLE
TEXTCOLOR = RED
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = RED
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = RED

XBORDER = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YBORDER = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Пятнашки')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    # создание доп. кнопок для игры
    RESET_SURF, RESET_RECT = makeText('Сброс', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    NEW_SURF, NEW_RECT = makeText('Новая игра', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = makeText('Решить', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)

    mainBoard, solutionSeq = generateNewPuzzle(80)
    SOLVEDBOARD = getStartingBoard()
    allMoves = []
    # основной цикл игры
    while True:
        slideTo = None  # направление движения плитки (изначально None, потом будет задаватся)
        msg = 'Нажимайте на плитку или на клавиши со стрелками(WASD).'
        if mainBoard == SOLVEDBOARD:
            msg = 'Готово!'

        drawBoard(mainBoard, msg)

        checkForQuit()
        for event in pygame.event.get():  # создание кликабительности кнопок
            if event.type == MOUSEBUTTONUP:                 # x             y
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves)
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80)
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq + allMoves)
                        allMoves = []
                else:

                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo:
            slideAnimation(mainBoard, slideTo, 'Нажимайте на плитку или на клавиши со стрелками(WASD).',
                           8)
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():  # бездействие и завершение программы
    pygame.quit()
    sys.exit()


def checkForQuit():  # функция, проверяющая события выхода из всех событий
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)


def getStartingBoard():  # создает структуру решенной головомки и возвращает её
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH - 1][BOARDHEIGHT - 1] = BLANK
    return board


def getBlankPosition(board):  # нахождение пустой клетки
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move): #  обновление доски
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):  # проверка того, что клетка может скользить в определенном направлении
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):  # определение ходов для перемешивания головомки
    validMoves = [UP, DOWN, LEFT, RIGHT]

    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):  # преобразует координаты на доске в координаты пикселей
    left = XBORDER + (tileX * TILESIZE) + (tileX - 1)
    top = YBORDER + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):  # выполняет противоположную функцию функции getLeftTopOfTile()
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):  # рисует на доске одну пронумерованную плитку
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top,
             left):  # обрабатывает создание объектов Surface и Rect для размещения текста на экране
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message): #  вывод доски на экран
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)


def slideAnimation(board, direction, message, animationSpeed):  # анимация скольжения плитки
    blankx, blanky = getBlankPosition(board)
    if direction == UP:  # проверка на возможность перемещения плитки
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()  # метод copy() вернет новый объект поверхности
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):  # решает головомку с помощью getStartingBoard() и запутывает снова
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500)
    lastMove = None
    for i in range(numSlides):  # numSlides - кол-во случайных ходов, которые нужно сделать
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Создание новой головоломки...', animationSpeed=int(TILESIZE / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)


def resetAnimation(board, allMoves):  # меняет все сделанные ходы местами, чтобы решить головоломку
    revAllMoves = allMoves[:]
    revAllMoves.reverse()

    for move in revAllMoves:  # отражение ходов для решения головомки
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', animationSpeed=int(TILESIZE / 2))
        makeMove(board, oppositeMove)


if __name__ == '__main__':
    main()
