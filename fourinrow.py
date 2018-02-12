#-*-coding:utf-8-*-
#!/usr/bin/python
import random, copy, sys, pygame
from pygame.locals import *

BOARDWIDTH = 7  # 棋子盘的宽度栏数
BOARDHEIGHT = 6 # 棋子盘的高度栏数
assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'

#python assert断言是声明其布尔值必须为真的判定，如果发生异常就说明表达示为假。
#可以理解assert断言语句为raise-if-not，用来测试表示式，其返回值为假，就会触发异常。

DIFFICULTY = 2 # 难度系数，计算机能够考虑的移动级别
               #这里2表示，考虑对手走棋的7种可能性及如何应对对手的7种走法

SPACESIZE = 50 # 棋子的大小

FPS = 30 # 屏幕的更新频率，即30/s
WINDOWWIDTH = 640  # 游戏屏幕的宽度像素
WINDOWHEIGHT = 480 # 游戏屏幕的高度像素

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)#X边缘坐标量，即格子栏的最左边
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)#Y边缘坐标量，即格子栏的最上边
BRIGHTBLUE = (0, 50, 255)#蓝色
WHITE = (255, 255, 255)#白色

BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

RED = 'red'
BLACK = 'black'
EMPTY = None
HUMAN = 'human'
COMPUTER = 'computer'


def main():
    global FPSCLOCK, DISPLAYSURF, REDPILERECT, BLACKPILERECT, REDTOKENIMG
    global BLACKTOKENIMG, BOARDIMG, ARROWIMG, ARROWRECT, HUMANWINNERIMG
    global COMPUTERWINNERIMG, WINNERRECT, TIEWINNERIMG

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    #创建游戏窗口
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    #游戏窗口标题
    pygame.display.set_caption('Four in a Row')
    REDPILERECT = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    #创建窗口左下和右下角的棋子
    BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    #载入红色棋子图片
    REDTOKENIMG = pygame.image.load('images/4rowred.png')    
    #将红色棋子图片缩放为SPACESIZE
    REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
    #黑色棋子
    BLACKTOKENIMG = pygame.image.load('images/4rowblack.png')
    #将黑色棋子图片缩放为SPACESIZE
    BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
    #载入棋子面板图片
    BOARDIMG = pygame.image.load('images/4rowboard.png')
    #将棋子面板图片缩放为SPACESIZE
    BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))
    #载入人胜利时图片
    HUMANWINNERIMG = pygame.image.load('images/4rowhumanwinner.png')
    #载入AI胜利时图片
    COMPUTERWINNERIMG = pygame.image.load('images/4rowcomputerwinner.png')
    #载入平局图片
    TIEWINNERIMG = pygame.image.load('images/4rowtie.png')
    #返回Rect实例
    WINNERRECT = HUMANWINNERIMG.get_rect()
    #游戏窗口中间位置坐标
    WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    #载入操作提示图片
    ARROWIMG = pygame.image.load('images/4rowarrow.png')
    #返回Rect实例
    ARROWRECT = ARROWIMG.get_rect()
    #操作提示的左位置
    ARROWRECT.left = REDPILERECT.right + 10 
    #将操作提示与下方红色棋子实例在纵向对齐
    ARROWRECT.centery = REDPILERECT.centery 

    isFirstGame = True 

    while True:
        runGame(isFirstGame)
        isFirstGame = False

def runGame(isFirstGame):
    if isFirstGame:
        turn = COMPUTER
        showHelp = True
    else:
        if random.randint(0, 1) == 0:
            turn = COMPUTER
        else:
            turn = HUMAN
        showHelp = False
    mainBoard = getNewBoard()
    while True:
        if isBoardFull(mainBoard):
            winnerImg = TIEWINNERIMG
            break 
        if turn == HUMAN:
            getHumanMove(mainBoard, showHelp)
            if showHelp:
                showHelp = False
            if isWinner(mainBoard, RED):
                winnerImg = HUMANWINNERIMG
                break
            turn = COMPUTER 
        else:
            column = getComputerMove(mainBoard)
            animateComputerMoving(mainBoard, column)
            makeMove(mainBoard, BLACK, column)
            if isWinner(mainBoard, BLACK):
                winnerImg = COMPUTERWINNERIMG
                break
            turn = HUMAN 

    while True:
        drawBoard(mainBoard)
        DISPLAYSURF.blit(winnerImg, WINNERRECT)
        pygame.display.update()
        FPSCLOCK.tick()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                return


def makeMove(board, player, column):
    lowest = getLowestEmptySpace(board, column)
    if lowest != -1:
        board[column][lowest] = player


def drawBoard(board, extraToken=None):
    #DISPLAYSURF 是我们的界面，在初始化变量模块中有定义
    DISPLAYSURF.fill(BGCOLOR)#将游戏窗口背景色填充为蓝色
    spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)#创建Rect实例
    for x in range(BOARDWIDTH):
        #确定每一列中每一行中的格子的左上角的位置坐标
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))

            #x =0,y =0时，即第一列第一行的格子。
            if board[x][y] == RED:#如果格子值为红色
                #则在在游戏窗口的spaceRect中画红色棋子
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[x][y] == BLACK: #否则画黑色棋子
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)

    # extraToken 是包含了位置信息和颜色信息的变量
    # 用来显示指定的棋子
    if extraToken != None:
        if extraToken['color'] == RED:
            DISPLAYSURF.blit(REDTOKENIMG,(extraToken['x'],
            extraToken['y'], SPACESIZE, SPACESIZE))
        elif extraToken['color'] == BLACK:
            DISPLAYSURF.blit(BLACKTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))

    # 画棋子面板
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            DISPLAYSURF.blit(BOARDIMG, spaceRect)

    # 画游戏窗口中左下角和右下角的棋子
    DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT) # 左边的红色棋子
    DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT) # 右边的黑色棋子

def getNewBoard():
    board = []
    for x in range(BOARDWIDTH):
        board.append([EMPTY] * BOARDHEIGHT)
    return board #返回board列表，其值为BOARDHEIGHT数量的None


def getHumanMove(board, isFirstMove):
    draggingToken = False
    tokenx, tokeny = None, None
    while True:
        # pygame.event.get()来处理所有的事件
        for event in pygame.event.get(): 
            #停止，退出
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #如果事件类型为鼠标按下，notdraggingToken为True，鼠标点击的位置在REDPILERECT里面
            elif event.type == MOUSEBUTTONDOWN and not draggingToken and REDPILERECT.collidepoint(event.pos):
                draggingToken = True
                tokenx, tokeny = event.pos
            #如果开始拖动了红色棋子
            elif event.type == MOUSEMOTION and draggingToken:
                #更新被拖拽的棋子的位置
                tokenx, tokeny = event.pos
            elif event.type == MOUSEBUTTONUP and draggingToken:
                #如果棋子被拖拽在board的正上方
                if tokeny < YMARGIN and tokenx > XMARGIN and tokenx < WINDOWWIDTH - XMARGIN:
                    #根据棋子的x坐标确定棋子会落的列(0,1...6)
                    column = int((tokenx - XMARGIN) / SPACESIZE)
                    if isValidMove(board, column):
                        #棋子掉落，显示掉落效果
                        animateDroppingToken(board, column, RED)
                        #将空格中最下面的格子设为红色
                        board[column][getLowestEmptySpace(board, column)] = RED
                        #落入的格子中划红色棋子
                        drawBoard(board)
                        #窗口更新
                        pygame.display.update()
                        return
                tokenx, tokeny = None, None
                draggingToken = False
        if tokenx != None and tokeny != None:
            #如果拖动了棋子,则显示拖动的棋子，并且通过调整x,y的坐标使拖动时，鼠标始终位于棋子的中心位置。
            drawBoard(board, {'x':tokenx - int(SPACESIZE / 2), 'y':tokeny - int(SPACESIZE / 2), 'color':RED})
        else:
            #当为无效移动时，鼠标松开后，因为此时board中所有格子的值均为none
            #调用drawBoard时，进行的操作是显示下面的两个棋子，相当于棋子回到到开始拖动的地方
            drawBoard(board)

        if isFirstMove:
            #AI先走，显示提示操作图片
            DISPLAYSURF.blit(ARROWIMG, ARROWRECT)

        pygame.display.update()
        FPSCLOCK.tick()


def animateDroppingToken(board, column, color):
    x = XMARGIN + column * SPACESIZE
    y = YMARGIN - SPACESIZE
    dropSpeed = 1.0#棋子降落的速度

    lowestEmptySpace = getLowestEmptySpace(board, column)

    while True:
        y += int(dropSpeed)#y的坐标以dropSpeed叠加
        dropSpeed += 0.5#dropSpeed也在加速，即棋子下落的加速度为0.5
        #判断到达最下面的空格
        if int((y - YMARGIN) / SPACESIZE) >= lowestEmptySpace:
            return
        #y不断变化，不断绘制红色棋子，形成不断降落的效果
        drawBoard(board, {'x':x, 'y':y, 'color':color})
        pygame.display.update()
        FPSCLOCK.tick()


def animateComputerMoving(board, column):
    x = BLACKPILERECT.left
    y = BLACKPILERECT.top
    speed = 1.0
    while y > (YMARGIN - SPACESIZE):
        y -= int(speed)
        speed += 0.5
        drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    y = YMARGIN - SPACESIZE
    speed = 1.0
    while x > (XMARGIN + column * SPACESIZE):
        x -= int(speed)
        speed += 0.5
        drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    animateDroppingToken(board, column, BLACK)


def getComputerMove(board):
    potentialMoves = getPotentialMoves(board, BLACK, DIFFICULTY)                               
    bestMoves = []
    bestMoveFitness = -BOARDWIDTH
    for i in range(len(potentialMoves)):
        if potentialMoves[i]>bestMoveFitness and isValidMove(board,i):
            bestMoveFitness = potentialMoves[i]                                                     
    for i in range(len(potentialMoves)):        
        if potentialMoves[i] == bestMoveFitness and isValidMove(board, i):
            bestMoves.append(i)   
    return random.choice(bestMoves)


def getPotentialMoves(board, tile, depth):
    if depth == 0 or isBoardFull(board):
        return [0] * BOARDWIDTH
    #确定对手棋子颜色
    if tile == RED:
        enemyTile = BLACK
    else:
        enemyTile = RED
    #初始一个潜在的移动列表，其数值全部为0
    potentialMoves = [0] * BOARDWIDTH
    for firstMove in range(BOARDWIDTH):
        #对每一栏进行遍历，将双方中的任一方的移动称为firstMove
        #则另外一方的移动就称为对手，counterMove。
        #这里我们的firstMove为AI，对手为玩家。
        dupeBoard = copy.deepcopy(board)#可换成回溯的方式，那样就不用每次都深拷贝了
        #这里用深复制是为了让board和dupeBoard不互相影响
        if not isValidMove(dupeBoard, firstMove):
            continue
        #如果是有效移动，则设置相应的格子颜色
        makeMove(dupeBoard, tile, firstMove)
        if isWinner(dupeBoard, tile):
            potentialMoves[firstMove] = 1
            #获胜的棋子自动获得一个很高的数值来表示其获胜的几率
            #数值越大，获胜可能性越大，对手获胜可能性越小。
            break
            #不要干扰计算其他的移动 
        else:
            if isBoardFull(dupeBoard):
                #如果dupeBoard中没有空格，无法移动
                potentialMoves[firstMove] = 0
            else:
                for counterMove in range(BOARDWIDTH):
                    #考虑对手移动
                    dupeBoard2 = copy.deepcopy(dupeBoard)
                    if not isValidMove(dupeBoard2, counterMove):
                        continue

                    makeMove(dupeBoard2, enemyTile, counterMove)
                    #玩家获胜
                    if isWinner(dupeBoard2, enemyTile):
                        potentialMoves[firstMove] = -1
                        break
                    else:
                        #递归调用
                        results = getPotentialMoves(dupeBoard2, tile, depth - 1)
                        potentialMoves[firstMove] += (sum(results)*1.0 / BOARDWIDTH) / BOARDWIDTH #求适应度fitness
    return potentialMoves


def getLowestEmptySpace(board, column):
    for y in range(BOARDHEIGHT-1, -1, -1):
        if board[column][y] == EMPTY:
            return y
    return -1


def isValidMove(board, column):
    if column < 0 or column >= (BOARDWIDTH) or board[column][0] != EMPTY:
        return False
    return True


def isBoardFull(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == EMPTY:
                return False
    return True


def isWinner(board, tile):
    for x in range(BOARDWIDTH - 3):
        for y in range(BOARDHEIGHT):
            if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
                return True
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT - 3):
            if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
                return True
    for x in range(BOARDWIDTH - 3):
        for y in range(3, BOARDHEIGHT):
            if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
                return True
    for x in range(BOARDWIDTH - 3):
        for y in range(BOARDHEIGHT - 3):
            if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
                return True
    return False


if __name__ == '__main__':
    main()

